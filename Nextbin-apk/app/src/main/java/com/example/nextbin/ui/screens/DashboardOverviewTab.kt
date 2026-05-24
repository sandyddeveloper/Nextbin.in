package com.example.nextbin.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.api.*
import com.example.nextbin.theme.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun DashboardOverviewTab(
    refreshTrigger: Int,
    onViewAllAuditLogs: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(true) }
    var monitorsCount by remember { mutableStateOf(0) }
    var upMonitors by remember { mutableStateOf(0) }
    var downMonitors by remember { mutableStateOf(0) }
    var igCount by remember { mutableStateOf(0) }
    var connectedIg by remember { mutableStateOf(0) }
    var issueIg by remember { mutableStateOf(0) }
    var auditLogs by remember { mutableStateOf<List<AuditLog>>(emptyList()) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    fun loadData() {
        scope.launch {
            isLoading = true
            errorMessage = null
            try {
                val service = ApiClient.getService()

                val projectsRes = service.getProjects()
                val projects = projectsRes.data
                monitorsCount = projects.size
                upMonitors = projects.count { it.lastStatus == "UP" }
                downMonitors = projects.count { it.lastStatus == "DOWN" }

                val accountsRes = service.getInstagramAccounts()
                val accounts = accountsRes.data
                igCount = accounts.size
                connectedIg = accounts.count { it.status == "CONNECTED" }
                issueIg = accounts.count { it.status == "ERROR" || it.status == "2FA_REQUIRED" }

                val logsResponse = service.getAuditLogs(skip = 0, limit = 10)
                auditLogs = logsResponse.data.data
            } catch (e: Exception) {
                errorMessage = e.toApiErrorMessage()
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(refreshTrigger) {
        loadData()
    }

    if (isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(color = Primary)
        }
    } else if (errorMessage != null) {
        Box(modifier = Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(errorMessage!!, color = DownRed, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = { loadData() }, colors = ButtonDefaults.buttonColors(containerColor = Primary)) {
                    Text("Retry")
                }
            }
        }
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Stats Row
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("SYSTEM OVERVIEW", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    
                    // Web Monitors Card
                    StatCard(
                        title = "Web Monitors",
                        value = monitorsCount.toString(),
                        subtext = "${upMonitors} UP  •  ${downMonitors} DOWN",
                        icon = Icons.Default.Assessment,
                        accentColor = Primary
                    )

                    // Instagram Agents Card
                    StatCard(
                        title = "Instagram Agents",
                        value = igCount.toString(),
                        subtext = "${connectedIg} Connected  •  ${issueIg} Issues",
                        icon = Icons.Default.Forum,
                        accentColor = Color(0xFFEC4899)
                    )

                    // Security Events Card
                    StatCard(
                        title = "Security Events",
                        value = auditLogs.size.toString(),
                        subtext = if (auditLogs.isNotEmpty()) (auditLogs.first().action ?: "No recent events") else "No recent events",
                        icon = Icons.Default.Shield,
                        accentColor = CyanAccent
                    )
                }
            }

            // Recent Audit Stream
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(SurfaceCard, shape = RoundedCornerShape(16.dp))
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("RECENT AUDIT STREAM", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "Top 5 recent security events from your system",
                            color = Color.LightGray,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                    TextButton(onClick = onViewAllAuditLogs) {
                        Text("See more", color = Primary, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = "See more",
                            tint = Primary,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }

            if (auditLogs.isEmpty()) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(100.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("No audit events recorded", color = Color.Gray, fontSize = 13.sp)
                    }
                }
            } else {
                items(auditLogs.take(5)) { log ->
                    AuditStreamItem(log = log)
                }
            }
        }
    }
}

@Composable
fun StatCard(
    title: String,
    value: String,
    subtext: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    accentColor: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF1E293B)))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(accentColor.copy(alpha = 0.15f), shape = RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(imageVector = icon, contentDescription = title, tint = accentColor, modifier = Modifier.size(24.dp))
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(text = title, color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                Text(text = value, color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Black)
                Text(text = subtext, color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.Normal)
            }
        }
    }
}

@Composable
fun AuditStreamItem(log: AuditLog) {
    // Parse time robustly
    val formattedTime = formatAuditTime(log.createdAt)

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Surface),
        border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF1E293B)))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = log.action ?: "UNKNOWN",
                    color = Primary,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = formattedTime,
                    color = Color.Gray,
                    fontSize = 11.sp
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = log.ipAddress ?: "0.0.0.0",
                    color = Color.LightGray,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = log.platform?.uppercase(Locale.getDefault()) ?: "MOBILE",
                    color = Color.DarkGray,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Black
                )
            }
        }
    }
}

fun formatAuditTime(rawTime: String?): String {
    if (rawTime.isNullOrBlank()) return ""
    val formats = listOf(
        "yyyy-MM-dd'T'HH:mm:ss.SSS",
        "yyyy-MM-dd'T'HH:mm:ss",
        "yyyy-MM-dd HH:mm:ss",
        "yyyy-MM-dd'T'HH:mm",
        "yyyy-MM-dd"
    )
    for (format in formats) {
        try {
            val inputFormat = SimpleDateFormat(format, Locale.getDefault())
            val date = inputFormat.parse(rawTime)
            if (date != null) {
                val outputFormat = SimpleDateFormat("hh:mm a", Locale.getDefault())
                return outputFormat.format(date)
            }
        } catch (e: Exception) {
            // continue
        }
    }
    // Fallback split parsing
    try {
        val parts = rawTime.split(Regex("[T ]"))
        if (parts.size > 1) {
            val timePart = parts[1]
            return if (timePart.length >= 5) timePart.substring(0, 5) else timePart
        }
        if (rawTime.length >= 5) {
            return rawTime.substring(0, 5)
        }
    } catch (e: Exception) {}
    return rawTime
}
