package com.example.nextbin.data.api

import com.google.gson.annotations.SerializedName
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

// ==========================================
// 1. Data Models (API Requests & Responses)
// ==========================================

data class LoginResponseWrapper(
    val status: String,
    val message: String,
    val data: TokenResponse
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String
)

data class UserResponse(
    val id: Int,
    val email: String?,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("is_active") val isActive: Boolean?,
    @SerializedName("is_superuser") val isSuperuser: Boolean?
)

data class UserUpdate(
    val email: String? = null,
    val password: String? = null,
    @SerializedName("full_name") val fullName: String? = null
)

data class MonitoredProject(
    val id: Int,
    val name: String?,
    val url: String?,
    @SerializedName("is_active") val isActive: Boolean?,
    @SerializedName("check_interval_seconds") val checkIntervalSeconds: Int?,
    @SerializedName("expected_status_code") val expectedStatusCode: Int?,
    @SerializedName("last_status") val lastStatus: String?,
    @SerializedName("last_checked_at") val lastCheckedAt: String?,
    @SerializedName("last_error") val lastError: String?
)

data class MonitoredProjectCreate(
    val name: String,
    val url: String,
    @SerializedName("is_active") val isActive: Boolean = true,
    @SerializedName("check_interval_seconds") val checkIntervalSeconds: Int = 300,
    @SerializedName("expected_status_code") val expectedStatusCode: Int = 200
)

data class MonitoredProjectUpdate(
    val name: String? = null,
    val url: String? = null,
    @SerializedName("is_active") val isActive: Boolean? = null,
    @SerializedName("check_interval_seconds") val checkIntervalSeconds: Int? = null,
    @SerializedName("expected_status_code") val expectedStatusCode: Int? = null
)

data class PerformanceMetric(
    val id: Int,
    @SerializedName("project_id") val projectId: Int,
    @SerializedName("response_time_ms") val responseTimeMs: Int,
    @SerializedName("status_code") val statusCode: Int?,
    @SerializedName("ssl_days_remaining") val sslDaysRemaining: Int?,
    @SerializedName("is_up") val isUp: Boolean?,
    @SerializedName("error_message") val errorMessage: String?,
    val timestamp: String?
)

data class InstagramAccount(
    val id: Int,
    val username: String?,
    @SerializedName("is_active") val isActive: Boolean?,
    val status: String?,
    @SerializedName("last_synced_at") val lastSyncedAt: String?
)

data class InstagramAccountCreate(
    val username: String,
    val password: String,
    @SerializedName("is_active") val isActive: Boolean = true
)

data class InstagramRule(
    val id: Int,
    @SerializedName("account_id") val accountId: Int,
    @SerializedName("trigger_keyword") val triggerKeyword: String?,
    @SerializedName("response_text") val responseText: String?,
    @SerializedName("is_active") val isActive: Boolean?
)

data class InstagramRuleCreate(
    @SerializedName("trigger_keyword") val triggerKeyword: String,
    @SerializedName("response_text") val responseText: String,
    @SerializedName("is_active") val isActive: Boolean = true
)

data class InstagramChatLog(
    val id: Int,
    @SerializedName("account_id") val accountId: Int,
    @SerializedName("thread_id") val threadId: String?,
    @SerializedName("message_id") val messageId: String?,
    @SerializedName("sender_username") val senderUsername: String?,
    val text: String?,
    val direction: String?, // INCOMING, OUTGOING
    val timestamp: String?
)

data class AuditLog(
    val id: Int,
    @SerializedName("user_id") val userId: Int?,
    val action: String?,
    @SerializedName("request_id") val requestId: String?,
    val platform: String?,
    @SerializedName("ip_address") val ipAddress: String?,
    val details: com.google.gson.JsonElement?,
    @SerializedName("created_at") val createdAt: String?
)
// Standardized API wrapper used by the server middleware: { status, message, data }
data class ApiListProjects(
    val status: String,
    val message: String,
    val data: List<MonitoredProject>
)

data class ApiListInstagramAccounts(
    val status: String,
    val message: String,
    val data: List<InstagramAccount>
)

data class ApiListAuditLogs(
    val status: String,
    val message: String,
    val data: AuditLogsPage
)

data class AuditLogsPage(
    val total: Int,
    val skip: Int,
    val limit: Int,
    val data: List<AuditLog>
)

data class LogFileResponse(
    val file: String,
    val lines: List<String>
)

data class AllLogFilesResponse(
    val files: List<String>,
    val logs: Map<String, List<String>>
)

data class ApiListPerformanceMetric(
    val status: String,
    val message: String,
    val data: List<PerformanceMetric>
)

// Generic wrapper matching server middleware output: { status, message, data }
data class ApiWrapper<T>(
    val status: String,
    val message: String,
    val data: T
)


// ==========================================
// 2. Retrofit API Service Interface
// ==========================================

interface ApiService {

    // Auth
    @Headers("Content-Type: application/json")
    @POST("api/v1/auth/login")
    suspend fun login(
        @Body request: com.google.gson.JsonObject
    ): LoginResponseWrapper

    @GET("api/v1/auth/me")
    suspend fun getMe(): ApiWrapper<UserResponse>

    @PUT("api/v1/auth/me")
    suspend fun updateMe(
        @Body update: UserUpdate
    ): ApiWrapper<UserResponse>

    @GET("api/v1/auth/audit-logs")
    suspend fun getAuditLogs(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 10
    ): ApiListAuditLogs

    @GET("api/v1/admin/logs/api")
    suspend fun getApiLogs(
        @Query("lines") lines: Int = 10
    ): ApiWrapper<LogFileResponse>

    @GET("api/v1/admin/logs/error")
    suspend fun getErrorLogs(
        @Query("lines") lines: Int = 10
    ): ApiWrapper<LogFileResponse>

    @GET("api/v1/admin/logs/all")
    suspend fun getAllLogs(
        @Query("lines") lines: Int = 10
    ): ApiWrapper<AllLogFilesResponse>

    // Web Monitors
    @GET("api/v1/projects/")
    suspend fun getProjects(): ApiListProjects

    @POST("api/v1/projects/")
    suspend fun createProject(
        @Body project: MonitoredProjectCreate
    ): ApiWrapper<MonitoredProject>

    @GET("api/v1/projects/{project_id}")
    suspend fun getProject(
        @Path("project_id") projectId: Int
    ): ApiWrapper<MonitoredProject>

    @PUT("api/v1/projects/{project_id}")
    suspend fun updateProject(
        @Path("project_id") projectId: Int,
        @Body project: MonitoredProjectUpdate
    ): ApiWrapper<MonitoredProject>

    @DELETE("api/v1/projects/{project_id}")
    suspend fun deleteProject(
        @Path("project_id") projectId: Int
    ): Response<Unit>

    @GET("api/v1/projects/{project_id}/metrics")
    suspend fun getProjectMetrics(
        @Path("project_id") projectId: Int,
        @Query("limit") limit: Int = 100
    ): ApiListPerformanceMetric

    @POST("api/v1/projects/{project_id}/trigger")
    suspend fun triggerManualPing(
        @Path("project_id") projectId: Int
    ): ApiWrapper<Map<String, String>>

    // Instagram Accounts
    @GET("api/v1/instagram/accounts")
    suspend fun getInstagramAccounts(): ApiListInstagramAccounts

    @POST("api/v1/instagram/accounts")
    suspend fun linkInstagramAccount(
        @Body account: InstagramAccountCreate
    ): ApiWrapper<InstagramAccount>

    @DELETE("api/v1/instagram/accounts/{account_id}")
    suspend fun deleteInstagramAccount(
        @Path("account_id") accountId: Int
    ): Response<Unit>

    @POST("api/v1/instagram/accounts/{account_id}/connect")
    suspend fun triggerAccountConnection(
        @Path("account_id") accountId: Int
    ): ApiWrapper<Map<String, String>>

    // Instagram Rules
    @GET("api/v1/instagram/accounts/{account_id}/rules")
    suspend fun getInstagramRules(
        @Path("account_id") accountId: Int
    ): ApiWrapper<List<InstagramRule>>

    @POST("api/v1/instagram/accounts/{account_id}/rules")
    suspend fun createInstagramRule(
        @Path("account_id") accountId: Int,
        @Body rule: InstagramRuleCreate
    ): ApiWrapper<InstagramRule>

    // Instagram Logs
    @GET("api/v1/instagram/accounts/{account_id}/logs")
    suspend fun getInstagramChatLogs(
        @Path("account_id") accountId: Int
    ): ApiWrapper<List<InstagramChatLog>>

    // Send DM (FastAPI expects thread_id and text as query parameters)
    @POST("api/v1/instagram/accounts/{account_id}/send-dm")
    suspend fun sendDirectMessage(
        @Path("account_id") accountId: Int,
        @Query("thread_id") threadId: String,
        @Query("text") text: String
    ): ApiWrapper<Map<String, String>>
}

// ==========================================
// 3. ApiClient Dynamic Singleton Wrapper
// ==========================================

object ApiClient {
    private var activeToken: String? = null
    var baseUrl: String = "http://10.0.2.2:8000/" // Trailing slash is mandatory in Retrofit

    fun setAuthToken(token: String?) {
        activeToken = token
    }

    private fun getOkHttpClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val originalRequest = chain.request()
                val requestBuilder = originalRequest.newBuilder()
                
                // Inject bearer token if available
                activeToken?.let { token ->
                    requestBuilder.addHeader("Authorization", "Bearer $token")
                }
                
                // Enforce Platform Header. Send 'web' to support live servers that only allow 'web' or 'ios'
                requestBuilder.addHeader("X-Platform", "web")
                
                chain.proceed(requestBuilder.build())
            }
            .addInterceptor(logging)
            .build()
    }

    fun getService(): ApiService {
        // Trim spaces, remove trailing colons and slashes, then enforce trailing slash
        var sanitizedUrl = baseUrl.trim()
        while (sanitizedUrl.endsWith(":") || sanitizedUrl.endsWith("/")) {
            sanitizedUrl = sanitizedUrl.substring(0, sanitizedUrl.length - 1).trim()
        }
        sanitizedUrl = "$sanitizedUrl/"
        
        return Retrofit.Builder()
            .baseUrl(sanitizedUrl)
            .client(getOkHttpClient())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

// ==========================================
// 4. Standardized API Error Handling
// ==========================================

data class ApiErrorResponse(
    val status: String?,
    val message: String?,
    val errors: Any?,
    val detail: Any?
)

fun Throwable.toApiErrorMessage(): String {
    return when (this) {
        is retrofit2.HttpException -> {
            val errorBody = response()?.errorBody()?.string()
            try {
                val parsed = com.google.gson.Gson().fromJson(errorBody, ApiErrorResponse::class.java)
                
                // Handle complex detail fields
                if (parsed.detail is List<*>) {
                    return parsed.detail.joinToString("\n") { it.toString() }
                }
                
                parsed.message ?: parsed.detail?.toString() ?: "Error ${code()}: ${message()}"
            } catch (ex: Exception) {
                "Error ${code()}: ${message()}"
            }
        }
        is java.io.IOException -> "Server unreachable. Check your connection."
        else -> this.localizedMessage ?: "An unexpected error occurred."
    }
}
