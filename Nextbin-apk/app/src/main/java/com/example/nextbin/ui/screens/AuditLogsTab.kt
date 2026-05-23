package com.example.nextbin.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.api.ApiClient
import com.example.nextbin.data.api.AuditLog
import com.example.nextbin.data.api.toApiErrorMessage
import com.example.nextbin.theme.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun AuditLogsTab(refreshTrigger: Int) {
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(true) }
    var logs by remember { mutableStateOf<List<AuditLog>>(emptyList()) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    fun loadLogs() {
        scope.launch {
            isLoading = true
            errorMessage = null
            try {
                val service = ApiClient.getService()
                logs = service.getAuditLogs(limit = 100)
            } catch (e: Exception) {
                errorMessage = e.toApiErrorMessage()
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(refreshTrigger) {
        loadLogs()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Background)
    ) {
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = CyanAccent)
            }
        } else if (errorMessage != null) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(errorMessage!!, color = DownRed)
            }
        } else if (logs.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No security audit logs available.", color = Color.Gray)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(logs) { log ->
                    AuditLogItemCard(log = log)
                }
            }
        }
    }
}

@Composable
fun AuditLogItemCard(log: AuditLog) {
    var expanded by remember { mutableStateOf(false) }

    val isAlertAction = log.action.contains("FAILED") || log.action.contains("DELETED") || log.action.contains("UNLINKED")
    val actionColor = if (isAlertAction) DownRed else UpGreen

    val formattedDate = try {
        // Format e.g., 2026-05-24T03:59:14 -> 24 May 2026, 03:59 AM
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val outputFormat = SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.getDefault())
        val date = inputFormat.parse(log.createdAt.substring(0, 19))
        outputFormat.format(date!!)
    } catch (e: Exception) {
        log.createdAt.replace("T", " ")
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF1E293B)))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Icon(
                        imageVector = if (isAlertAction) Icons.Default.Warning else Icons.Default.Info,
                        contentDescription = "Log Level",
                        tint = actionColor,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = log.action,
                        color = actionColor,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Text(
                    text = log.platform?.uppercase(Locale.getDefault()) ?: "WEB",
                    color = Color.Gray,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Black
                )
            }

            Spacer(modifier = Modifier.height(4.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = log.ipAddress ?: "Unknown IP",
                    color = Color.LightGray,
                    fontSize = 11.sp
                )
                Text(
                    text = formattedDate,
                    color = Color.Gray,
                    fontSize = 10.sp
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(modifier = Modifier.padding(top = 12.dp)) {
                    Divider(color = Color(0xFF1E293B), modifier = Modifier.padding(bottom = 8.dp))
                    
                    Text("Metadata Details", color = Color.Gray, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF060910), shape = RoundedCornerShape(8.dp))
                            .padding(10.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        if (log.details.isNullOrEmpty()) {
                            Text("No extra details recorded.", color = Color.DarkGray, fontSize = 11.sp)
                        } else {
                            log.details.forEach { (key, value) ->
                                Row(modifier = Modifier.fillMaxWidth()) {
                                    Text(
                                        text = "$key: ",
                                        color = Primary,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.width(100.dp)
                                    )
                                    Text(
                                        text = value.toString(),
                                        color = Color.LightGray,
                                        fontSize = 11.sp,
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                            }
                        }

                        if (log.requestId != null) {
                            Row(modifier = Modifier.fillMaxWidth().padding(top = 6.dp)) {
                                Text(
                                    text = "Request ID: ",
                                    color = Color.DarkGray,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.width(100.dp)
                                )
                                Text(
                                    text = log.requestId,
                                    color = Color.DarkGray,
                                    fontSize = 10.sp,
                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
