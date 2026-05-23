package com.example.nextbin.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.api.ApiClient
import com.example.nextbin.data.api.toApiErrorMessage
import com.example.nextbin.data.api.MonitoredProject
import com.example.nextbin.data.api.MonitoredProjectCreate
import com.example.nextbin.data.api.PerformanceMetric
import com.example.nextbin.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MonitorsTab(refreshTrigger: Int) {
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(true) }
    var projects by remember { mutableStateOf<List<MonitoredProject>>(emptyList()) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    // Add Dialog State
    var showAddDialog by remember { mutableStateOf(false) }
    var newName by remember { mutableStateOf("") }
    var newUrl by remember { mutableStateOf("https://") }
    var newInterval by remember { mutableStateOf("300") }
    var newExpectedCode by remember { mutableStateOf("200") }
    var isSubmitting by remember { mutableStateOf(false) }

    fun loadProjects() {
        scope.launch {
            isLoading = true
            errorMessage = null
            try {
                val service = ApiClient.getService()
                projects = service.getProjects()
            } catch (e: Exception) {
                errorMessage = e.toApiErrorMessage()
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(refreshTrigger) {
        loadProjects()
    }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showAddDialog = true },
                containerColor = Primary,
                contentColor = Color.White,
                shape = CircleShape
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Monitor")
            }
        },
        containerColor = Background
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Background)
        ) {
            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = Primary)
                }
            } else if (errorMessage != null) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(errorMessage!!, color = DownRed)
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    if (projects.isEmpty()) {
                        item {
                            Box(
                                modifier = Modifier.fillParentMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                Text("No web monitors registered. Click + to add one.", color = Color.Gray, fontSize = 14.sp)
                            }
                        }
                    } else {
                        items(projects) { project ->
                            MonitorItemCard(project = project, onDelete = { loadProjects() }, onTrigger = { loadProjects() })
                        }
                    }
                }
            }

            // Create Monitor Overlay Dialog
            if (showAddDialog) {
                AlertDialog(
                    onDismissRequest = { if (!isSubmitting) showAddDialog = false },
                    title = { Text("New Web Monitor", color = Color.White, fontWeight = FontWeight.Bold) },
                    containerColor = SurfaceCard,
                    text = {
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            OutlinedTextField(
                                value = newName,
                                onValueChange = { newName = it },
                                label = { Text("Monitor Name") },
                                placeholder = { Text("e.g. My Website API") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Primary,
                                    unfocusedBorderColor = Color(0xFF1E293B),
                                    focusedLabelColor = Primary,
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            OutlinedTextField(
                                value = newUrl,
                                onValueChange = { newUrl = it },
                                label = { Text("Service URL") },
                                placeholder = { Text("https://example.com/api") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Primary,
                                    unfocusedBorderColor = Color(0xFF1E293B),
                                    focusedLabelColor = Primary,
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                                OutlinedTextField(
                                    value = newInterval,
                                    onValueChange = { newInterval = it },
                                    label = { Text("Interval (sec)") },
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                    modifier = Modifier.weight(1f),
                                    singleLine = true,
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = Primary,
                                        unfocusedBorderColor = Color(0xFF1E293B),
                                        focusedLabelColor = Primary,
                                        unfocusedLabelColor = Color.Gray,
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White
                                    )
                                )

                                OutlinedTextField(
                                    value = newExpectedCode,
                                    onValueChange = { newExpectedCode = it },
                                    label = { Text("Expected Status") },
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                    modifier = Modifier.weight(1f),
                                    singleLine = true,
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = Primary,
                                        unfocusedBorderColor = Color(0xFF1E293B),
                                        focusedLabelColor = Primary,
                                        unfocusedLabelColor = Color.Gray,
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White
                                    )
                                )
                            }
                        }
                    },
                    confirmButton = {
                        Button(
                            onClick = {
                                if (newName.isBlank() || newUrl.isBlank()) return@Button
                                scope.launch {
                                    isSubmitting = true
                                    try {
                                        val service = ApiClient.getService()
                                        service.createProject(
                                            MonitoredProjectCreate(
                                                name = newName,
                                                url = newUrl,
                                                checkIntervalSeconds = newInterval.toIntOrNull() ?: 300,
                                                expectedStatusCode = newExpectedCode.toIntOrNull() ?: 200
                                            )
                                        )
                                        newName = ""
                                        newUrl = "https://"
                                        showAddDialog = false
                                        loadProjects()
                                    } catch (e: Exception) {
                                        // Handle dialog errors
                                    } finally {
                                        isSubmitting = false
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Primary),
                            enabled = !isSubmitting
                        ) {
                            Text("Create")
                        }
                    },
                    dismissButton = {
                        TextButton(
                            onClick = { showAddDialog = false },
                            colors = ButtonDefaults.textButtonColors(contentColor = Color.Gray),
                            enabled = !isSubmitting
                        ) {
                            Text("Cancel")
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun MonitorItemCard(
    project: MonitoredProject,
    onDelete: () -> Unit,
    onTrigger: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    var metrics by remember { mutableStateOf<List<PerformanceMetric>>(emptyList()) }
    var isLoadingMetrics by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    val statusColor = when (project.lastStatus) {
        "UP" -> UpGreen
        "DOWN" -> DownRed
        else -> Color.Gray
    }

    LaunchedEffect(expanded) {
        if (expanded) {
            isLoadingMetrics = true
            try {
                val service = ApiClient.getService()
                metrics = service.getProjectMetrics(project.id, limit = 15)
            } catch (e: Exception) {
                // Ignore metrics errors
            } finally {
                isLoadingMetrics = false
            }
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF1E293B)))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = project.name,
                        color = Color.White,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = project.url,
                        color = Color.Gray,
                        fontSize = 11.sp,
                        modifier = Modifier.padding(top = 2.dp)
                    )
                }

                // Pulsing glow indicator
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .background(statusColor.copy(alpha = 0.3f), shape = CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(6.dp)
                            .background(statusColor, shape = CircleShape)
                    )
                }
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(modifier = Modifier.padding(top = 16.dp)) {
                    Divider(color = Color(0xFF1E293B), modifier = Modifier.padding(bottom = 12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("Interval", color = Color.Gray, fontSize = 10.sp)
                            Text("${project.checkIntervalSeconds}s", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                        Column {
                            Text("Expected Code", color = Color.Gray, fontSize = 10.sp)
                            Text("${project.expectedStatusCode}", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                        Column {
                            Text("Status", color = Color.Gray, fontSize = 10.sp)
                            Text(project.lastStatus, color = statusColor, fontSize = 12.sp, fontWeight = FontWeight.Black)
                        }
                    }

                    if (!project.lastError.isNullOrBlank()) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Last Error", color = Color.Gray, fontSize = 10.sp)
                        Text(
                            text = project.lastError,
                            color = DownRed,
                            fontSize = 11.sp,
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(Color(0x1FFF7171), shape = RoundedCornerShape(8.dp))
                                .padding(8.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Latency Stream (ms)", color = Color.Gray, fontSize = 10.sp)

                    if (isLoadingMetrics) {
                        Box(
                            modifier = Modifier.fillMaxWidth().height(100.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = Primary, modifier = Modifier.size(24.dp))
                        }
                    } else if (metrics.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(8.dp))
                        LatencyChart(metrics = metrics)
                    } else {
                        Box(
                            modifier = Modifier.fillMaxWidth().height(100.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("No latency logs available", color = Color.DarkGray, fontSize = 12.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Buttons
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        IconButton(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        service.triggerManualPing(project.id)
                                        onTrigger()
                                    } catch (e: Exception) {}
                                }
                            }
                        ) {
                            Icon(Icons.Default.PlayArrow, contentDescription = "Run Ping Now", tint = UpGreen)
                        }

                        IconButton(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        service.deleteProject(project.id)
                                        onDelete()
                                    } catch (e: Exception) {}
                                }
                            }
                        ) {
                            Icon(Icons.Default.Delete, contentDescription = "Delete Monitor", tint = DownRed)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun LatencyChart(metrics: List<PerformanceMetric>) {
    // Canvas dimensions will map: points on X-axis, response_time_ms on Y-axis
    val responseTimes = metrics.map { it.responseTimeMs.toFloat() }.reversed()
    val maxLatency = (responseTimes.maxOrNull() ?: 100f).coerceAtLeast(100f)

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
            .background(Color(0xFF060910), shape = RoundedCornerShape(10.dp))
            .padding(vertical = 8.dp, horizontal = 12.dp)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            if (responseTimes.size < 2) return@Canvas

            val width = size.width
            val height = size.height
            val stepX = width / (responseTimes.size - 1)
            
            val path = Path()
            val fillPath = Path()

            responseTimes.forEachIndexed { i, latency ->
                // Map latency: 0 = bottom, maxLatency = top
                // But in Canvas, 0,0 is top-left, so we invert Y coordinate: height - (value * height / max)
                val x = i * stepX
                val y = height - (latency / maxLatency * height)

                if (i == 0) {
                    path.moveTo(x, y)
                    fillPath.moveTo(x, height)
                    fillPath.lineTo(x, y)
                } else {
                    path.lineTo(x, y)
                    fillPath.lineTo(x, y)
                }
                
                if (i == responseTimes.size - 1) {
                    fillPath.lineTo(x, height)
                    fillPath.close()
                }
            }

            // Draw area gradient fill
            drawPath(
                path = fillPath,
                brush = Brush.verticalGradient(
                    colors = listOf(Primary.copy(alpha = 0.25f), Color.Transparent),
                    startY = 0f,
                    endY = height
                )
            )

            // Draw line
            drawPath(
                path = path,
                color = Primary,
                style = Stroke(width = 2.dp.toPx())
            )
        }
    }
}
