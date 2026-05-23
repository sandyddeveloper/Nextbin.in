package com.example.nextbin.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.api.*
import com.example.nextbin.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InstagramTab(refreshTrigger: Int) {
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(true) }
    var accounts by remember { mutableStateOf<List<InstagramAccount>>(emptyList()) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    // Linking states
    var showLinkDialog by remember { mutableStateOf(false) }
    var igUser by remember { mutableStateOf("") }
    var igPass by remember { mutableStateOf("") }
    var isLinking by remember { mutableStateOf(false) }

    fun loadAccounts() {
        scope.launch {
            isLoading = true
            errorMessage = null
            try {
                val service = ApiClient.getService()
                accounts = service.getInstagramAccounts()
            } catch (e: Exception) {
                errorMessage = e.toApiErrorMessage()
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(refreshTrigger) {
        loadAccounts()
    }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showLinkDialog = true },
                containerColor = Color(0xFFEC4899), // Pink
                contentColor = Color.White,
                shape = CircleShape
            ) {
                Icon(Icons.Default.Add, contentDescription = "Link Instagram Account")
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
                    CircularProgressIndicator(color = Color(0xFFEC4899))
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
                    if (accounts.isEmpty()) {
                        item {
                            Box(
                                modifier = Modifier.fillParentMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                Text("No Instagram accounts linked. Click + to link.", color = Color.Gray, fontSize = 14.sp)
                            }
                        }
                    } else {
                        items(accounts) { account ->
                            InstagramAccountCard(
                                account = account,
                                onDelete = { loadAccounts() },
                                onConnectTriggered = { loadAccounts() }
                            )
                        }
                    }
                }
            }

            // Link Account Dialog
            if (showLinkDialog) {
                AlertDialog(
                    onDismissRequest = { if (!isLinking) showLinkDialog = false },
                    title = { Text("Link Instagram Account", color = Color.White, fontWeight = FontWeight.Bold) },
                    containerColor = SurfaceCard,
                    text = {
                        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                            OutlinedTextField(
                                value = igUser,
                                onValueChange = { igUser = it },
                                label = { Text("Instagram Username") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Color(0xFFEC4899),
                                    unfocusedBorderColor = Color(0xFF1E293B),
                                    focusedLabelColor = Color(0xFFEC4899),
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            OutlinedTextField(
                                value = igPass,
                                onValueChange = { igPass = it },
                                label = { Text("Instagram Password") },
                                visualTransformation = PasswordVisualTransformation(),
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Color(0xFFEC4899),
                                    unfocusedBorderColor = Color(0xFF1E293B),
                                    focusedLabelColor = Color(0xFFEC4899),
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )
                        }
                    },
                    confirmButton = {
                        Button(
                            onClick = {
                                if (igUser.isBlank() || igPass.isBlank()) return@Button
                                scope.launch {
                                    isLinking = true
                                    try {
                                        val service = ApiClient.getService()
                                        service.linkInstagramAccount(
                                            InstagramAccountCreate(
                                                username = igUser,
                                                password = igPass
                                            )
                                        )
                                        igUser = ""
                                        igPass = ""
                                        showLinkDialog = false
                                        loadAccounts()
                                    } catch (e: Exception) {
                                        // Error linking
                                    } finally {
                                        isLinking = false
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEC4899)),
                            enabled = !isLinking
                        ) {
                            Text("Link")
                        }
                    },
                    dismissButton = {
                        TextButton(
                            onClick = { showLinkDialog = false },
                            colors = ButtonDefaults.textButtonColors(contentColor = Color.Gray),
                            enabled = !isLinking
                        ) {
                            Text("Cancel")
                        }
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InstagramAccountCard(
    account: InstagramAccount,
    onDelete: () -> Unit,
    onConnectTriggered: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    var chatLogs by remember { mutableStateOf<List<InstagramChatLog>>(emptyList()) }
    var replyRules by remember { mutableStateOf<List<InstagramRule>>(emptyList()) }
    
    // Sub-dialog overlay triggers
    var showChatLogsDialog by remember { mutableStateOf(false) }
    var showRulesDialog by remember { mutableStateOf(false) }
    var showSendDmDialog by remember { mutableStateOf(false) }

    val scope = rememberCoroutineScope()

    val statusColor = when (account.status) {
        "CONNECTED" -> UpGreen
        "DISCONNECTED" -> Color.Gray
        "ERROR", "2FA_REQUIRED" -> DownRed
        else -> Color.Gray
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
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(Color(0xFFEC4899).copy(alpha = 0.1f), shape = CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.Forum, contentDescription = "Instagram", tint = Color(0xFFEC4899), modifier = Modifier.size(18.dp))
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = "@${account.username}",
                            color = Color.White,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Status: ${account.status}",
                            color = statusColor,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                // Check active state
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(statusColor, shape = CircleShape)
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(modifier = Modifier.padding(top = 16.dp)) {
                    Divider(color = Color(0xFF1E293B), modifier = Modifier.padding(bottom = 12.dp))

                    // Primary Action Rows
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        service.triggerAccountConnection(account.id)
                                        onConnectTriggered()
                                    } catch (e: Exception) {}
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Primary),
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Text("Connect", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        chatLogs = service.getInstagramChatLogs(account.id)
                                        showChatLogsDialog = true
                                    } catch (e: Exception) {}
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E293B)),
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Text("Chats", fontSize = 12.sp, color = Color.White)
                        }

                        Button(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        replyRules = service.getInstagramRules(account.id)
                                        showRulesDialog = true
                                    } catch (e: Exception) {}
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E293B)),
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Text("Rules", fontSize = 12.sp, color = Color.White)
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        TextButton(
                            onClick = { showSendDmDialog = true },
                            colors = ButtonDefaults.textButtonColors(contentColor = Color(0xFFEC4899))
                        ) {
                            Icon(Icons.Default.Send, contentDescription = "Send Direct Message", modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Send DM", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }

                        IconButton(
                            onClick = {
                                scope.launch {
                                    try {
                                        val service = ApiClient.getService()
                                        service.deleteInstagramAccount(account.id)
                                        onDelete()
                                    } catch (e: Exception) {}
                                }
                            }
                        ) {
                            Icon(Icons.Default.Delete, contentDescription = "Unlink Account", tint = DownRed)
                        }
                    }
                }
            }
        }
    }

    // Chat Logs Dialog
    if (showChatLogsDialog) {
        AlertDialog(
            onDismissRequest = { showChatLogsDialog = false },
            title = { Text("Chat Logs (@${account.username})", color = Color.White) },
            containerColor = SurfaceCard,
            text = {
                Box(modifier = Modifier.height(300.dp).fillMaxWidth()) {
                    if (chatLogs.isEmpty()) {
                        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Text("No chat logs recorded yet.", color = Color.Gray)
                        }
                    } else {
                        LazyColumn(
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                            modifier = Modifier.fillMaxSize()
                        ) {
                            items(chatLogs) { log ->
                                ChatBubbleItem(log = log)
                            }
                        }
                    }
                }
            },
            confirmButton = {
                Button(onClick = { showChatLogsDialog = false }, colors = ButtonDefaults.buttonColors(containerColor = Primary)) {
                    Text("Close")
                }
            }
        )
    }

    // Send DM Dialog
    if (showSendDmDialog) {
        var dmThreadId by remember { mutableStateOf("") }
        var dmText by remember { mutableStateOf("") }
        var isSendingDm by remember { mutableStateOf(false) }

        AlertDialog(
            onDismissRequest = { if (!isSendingDm) showSendDmDialog = false },
            title = { Text("Compose Direct Message", color = Color.White) },
            containerColor = SurfaceCard,
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = dmThreadId,
                        onValueChange = { dmThreadId = it },
                        label = { Text("Thread ID / Target Username") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Primary,
                            unfocusedBorderColor = Color(0xFF1E293B),
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White
                        )
                    )

                    OutlinedTextField(
                        value = dmText,
                        onValueChange = { dmText = it },
                        label = { Text("Message Text") },
                        modifier = Modifier.fillMaxWidth(),
                        maxLines = 4,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Primary,
                            unfocusedBorderColor = Color(0xFF1E293B),
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White
                        )
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (dmThreadId.isBlank() || dmText.isBlank()) return@Button
                        scope.launch {
                            isSendingDm = true
                            try {
                                val service = ApiClient.getService()
                                service.sendDirectMessage(account.id, dmThreadId, dmText)
                                showSendDmDialog = false
                            } catch (e: Exception) {
                                // DM send error
                            } finally {
                                isSendingDm = false
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEC4899)),
                    enabled = !isSendingDm
                ) {
                    Text("Send")
                }
            },
            dismissButton = {
                TextButton(onClick = { showSendDmDialog = false }, enabled = !isSendingDm, colors = ButtonDefaults.textButtonColors(contentColor = Color.Gray)) {
                    Text("Cancel")
                }
            }
        )
    }

    // Rules Dialog Manager
    if (showRulesDialog) {
        var ruleKeyword by remember { mutableStateOf("") }
        var ruleResponse by remember { mutableStateOf("") }
        var isAddingRule by remember { mutableStateOf(false) }

        AlertDialog(
            onDismissRequest = { showRulesDialog = false },
            title = { Text("Auto-Reply Rules", color = Color.White) },
            containerColor = SurfaceCard,
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                    // Create Rule Form
                    Column(
                        modifier = Modifier
                            .background(Color(0xFF060910), shape = RoundedCornerShape(12.dp))
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text("Add New Rule", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                        OutlinedTextField(
                            value = ruleKeyword,
                            onValueChange = { ruleKeyword = it },
                            label = { Text("Keyword Trigger") },
                            placeholder = { Text("e.g. price") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = Primary,
                                unfocusedBorderColor = Color(0xFF1E293B),
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White
                            )
                        )
                        OutlinedTextField(
                            value = ruleResponse,
                            onValueChange = { ruleResponse = it },
                            label = { Text("Auto Reply Text") },
                            placeholder = { Text("It costs $20") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = Primary,
                                unfocusedBorderColor = Color(0xFF1E293B),
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White
                            )
                        )
                        Button(
                            onClick = {
                                if (ruleKeyword.isBlank() || ruleResponse.isBlank()) return@Button
                                scope.launch {
                                    isAddingRule = true
                                    try {
                                        val service = ApiClient.getService()
                                        service.createInstagramRule(
                                            account.id,
                                            InstagramRuleCreate(
                                                triggerKeyword = ruleKeyword,
                                                responseText = ruleResponse
                                            )
                                        )
                                        ruleKeyword = ""
                                        ruleResponse = ""
                                        
                                        // Reload list
                                        replyRules = service.getInstagramRules(account.id)
                                    } catch (e: Exception) {} finally {
                                        isAddingRule = false
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Primary),
                            modifier = Modifier.fillMaxWidth(),
                            enabled = !isAddingRule
                        ) {
                            Text("Add Rule", fontSize = 12.sp)
                        }
                    }

                    // Existing Rules List
                    Divider(color = Color(0xFF1E293B))
                    Text("Active Rules", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    Box(modifier = Modifier.height(150.dp)) {
                        if (replyRules.isEmpty()) {
                            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                Text("No reply rules configured", color = Color.DarkGray, fontSize = 12.sp)
                            }
                        } else {
                            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxSize()) {
                                items(replyRules) { rule ->
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .background(Color(0xFF060910), shape = RoundedCornerShape(8.dp))
                                            .padding(10.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column(modifier = Modifier.weight(1f)) {
                                            Text(text = "If text contains: \"${rule.triggerKeyword}\"", color = Color(0xFFEC4899), fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                            Text(text = "Reply: \"${rule.responseText}\"", color = Color.LightGray, fontSize = 11.sp)
                                        }
                                        Icon(Icons.Default.CheckCircle, contentDescription = "Active", tint = UpGreen, modifier = Modifier.size(16.dp))
                                    }
                                }
                            }
                        }
                    }
                }
            },
            confirmButton = {
                Button(onClick = { showRulesDialog = false }, colors = ButtonDefaults.buttonColors(containerColor = Primary)) {
                    Text("Done")
                }
            }
        )
    }
}

@Composable
fun ChatBubbleItem(log: InstagramChatLog) {
    val isIncoming = log.direction == "INCOMING"

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isIncoming) Arrangement.Start else Arrangement.End
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 240.dp)
                .background(
                    color = if (isIncoming) Color(0xFF1E293B) else Color(0xFFEC4899).copy(alpha = 0.2f),
                    shape = RoundedCornerShape(
                        topStart = 12.dp,
                        topEnd = 12.dp,
                        bottomStart = if (isIncoming) 0.dp else 12.dp,
                        bottomEnd = if (isIncoming) 12.dp else 0.dp
                    )
                )
                .padding(10.dp)
        ) {
            Text(
                text = if (isIncoming) "@${log.senderUsername}" else "You (NILA Auto)",
                color = if (isIncoming) Color.Gray else Color(0xFFEC4899),
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = log.text ?: "",
                color = Color.White,
                fontSize = 12.sp
            )
        }
    }
}
