package com.example.nextbin.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Article
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.api.ApiClient
import com.example.nextbin.data.api.toApiErrorMessage
import com.example.nextbin.theme.Background
import com.example.nextbin.theme.Primary
import com.example.nextbin.theme.SurfaceCard
import kotlinx.coroutines.launch

@Composable
fun LogsScreen() {
    val scope = rememberCoroutineScope()
    var selectedLogType by remember { mutableStateOf<String?>(null) }
    var logLines by remember { mutableStateOf<List<String>>(emptyList()) }
    var allLogs by remember { mutableStateOf<Map<String, List<String>>>(emptyMap()) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    fun clearResults() {
        logLines = emptyList()
        allLogs = emptyMap()
        errorMessage = null
    }

    fun loadApiLog() {
        scope.launch {
            isLoading = true
            selectedLogType = "API Logs"
            clearResults()
            try {
                val response = ApiClient.getService().getApiLogs()
                logLines = response.data.lines
            } catch (error: Throwable) {
                errorMessage = error.toApiErrorMessage()
            }
            isLoading = false
        }
    }

    fun loadErrorLog() {
        scope.launch {
            isLoading = true
            selectedLogType = "Error Logs"
            clearResults()
            try {
                val response = ApiClient.getService().getErrorLogs()
                logLines = response.data.lines
            } catch (error: Throwable) {
                errorMessage = error.toApiErrorMessage()
            }
            isLoading = false
        }
    }

    fun loadAllLogs() {
        scope.launch {
            isLoading = true
            selectedLogType = "All Logs"
            clearResults()
            try {
                val response = ApiClient.getService().getAllLogs()
                allLogs = response.data.logs
            } catch (error: Throwable) {
                errorMessage = error.toApiErrorMessage()
            }
            isLoading = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "Logs",
            fontSize = 28.sp,
            fontWeight = FontWeight.ExtraBold,
            color = Color.White
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = "Tap a card to fetch API, error, or aggregate log output from the backend.",
            fontSize = 14.sp,
            color = Color.LightGray
        )
        Spacer(modifier = Modifier.height(18.dp))

        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            LogActionCard(
                title = "API Logs",
                description = "Fetch the latest API log output.",
                icon = Icons.Default.Article,
                selected = selectedLogType == "API Logs",
                onClick = { loadApiLog() }
            )
            LogActionCard(
                title = "Error Logs",
                description = "Fetch backend error logs.",
                icon = Icons.Default.BugReport,
                selected = selectedLogType == "Error Logs",
                onClick = { loadErrorLog() }
            )
            LogActionCard(
                title = "All Logs",
                description = "Fetch all available log files and content.",
                icon = Icons.Default.Cloud,
                selected = selectedLogType == "All Logs",
                onClick = { loadAllLogs() }
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (isLoading) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                CircularProgressIndicator(color = Primary)
            }
        }

        if (!errorMessage.isNullOrBlank()) {
            Text(
                text = errorMessage ?: "Unable to load logs.",
                color = Color.Red,
                fontSize = 14.sp,
                modifier = Modifier.padding(top = 12.dp)
            )
        }

        if (logLines.isNotEmpty() || allLogs.isNotEmpty()) {
            Spacer(modifier = Modifier.height(16.dp))
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 32.dp),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceCard)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = selectedLogType ?: "Results",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    if (allLogs.isNotEmpty()) {
                        allLogs.forEach { (fileName, lines) ->
                            Text(
                                text = fileName,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Primary
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            lines.forEachIndexed { index, line ->
                                Text(
                                    text = "${index + 1}. $line",
                                    fontSize = 12.sp,
                                    color = Color.White
                                )
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                        }
                    } else {
                        logLines.forEachIndexed { index, line ->
                            Text(
                                text = "${index + 1}. $line",
                                fontSize = 12.sp,
                                color = Color.White
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun LogActionCard(
    title: String,
    description: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    selected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) Primary.copy(alpha = 0.18f) else SurfaceCard
        )
    ) {
        Row(
            modifier = Modifier
                .padding(18.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = if (selected) Primary else Color.Gray,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Color.White
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = description,
                    fontSize = 13.sp,
                    color = Color.LightGray
                )
            }
        }
    }
}
