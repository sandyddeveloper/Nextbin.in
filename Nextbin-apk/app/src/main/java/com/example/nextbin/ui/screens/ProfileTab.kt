package com.example.nextbin.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.PrefManager
import com.example.nextbin.data.api.*
import com.example.nextbin.theme.*
import kotlinx.coroutines.launch

@Composable
fun ProfileTab(
    refreshTrigger: Int,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    val prefManager = remember { PrefManager(context) }
    val clipboardManager = LocalClipboardManager.current
    val scope = rememberCoroutineScope()

    var user by remember { mutableStateOf<UserResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Edit states
    var nameInput by remember { mutableStateOf("") }
    var emailInput by remember { mutableStateOf("") }
    var passwordInput by remember { mutableStateOf("") }
    var isUpdating by remember { mutableStateOf(false) }
    var updateSuccess by remember { mutableStateOf(false) }
    var updateError by remember { mutableStateOf<String?>(null) }

    var tokenCopied by remember { mutableStateOf(false) }

    fun loadProfile() {
        scope.launch {
            isLoading = true
            errorMessage = null
            try {
                val service = ApiClient.getService()
                val profileRes = service.getMe()
                val profile = profileRes.data
                user = profile
                nameInput = profile.fullName ?: ""
                emailInput = profile.email ?: ""
            } catch (e: Exception) {
                errorMessage = e.toApiErrorMessage()
            } finally {
                isLoading = false
            }
        }
    }

    LaunchedEffect(refreshTrigger) {
        loadProfile()
    }

    if (isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(color = Primary)
        }
    } else if (errorMessage != null) {
        Box(modifier = Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(errorMessage!!, color = DownRed, textAlign = TextAlign.Center)
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = { loadProfile() }, colors = ButtonDefaults.buttonColors(containerColor = Primary)) {
                    Text("Retry")
                }
            }
        }
    } else {
        val initials = remember(user) {
            val name = user?.fullName
            if (!name.isNullOrBlank()) {
                name.split(" ")
                    .mapNotNull { it.firstOrNull() }
                    .joinToString("")
                    .uppercase()
                    .take(2)
            } else {
                user?.email?.take(2)?.uppercase() ?: "AD"
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 1. Profile Hero Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = Brush.linearGradient(listOf(BorderColor, Color(0xFF334155))))
            ) {
                Box(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                    Box(
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .size(100.dp)
                            .background(
                                brush = Brush.radialGradient(
                                    colors = listOf(Primary.copy(alpha = 0.2f), Color.Transparent)
                                ),
                                shape = CircleShape
                            )
                    )

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(72.dp)
                                .background(
                                    brush = Brush.linearGradient(listOf(Primary, CyanAccent)),
                                    shape = RoundedCornerShape(20.dp)
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = initials,
                                color = Color.White,
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Black
                            )
                        }

                        Column(modifier = Modifier.weight(1f)) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = user?.fullName ?: "Administrator",
                                    color = Color.White,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.weight(1f, fill = false)
                                )
                            }
                            Text(
                                text = user?.email ?: "",
                                color = Color.Gray,
                                fontSize = 12.sp
                            )

                            Spacer(modifier = Modifier.height(8.dp))

                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                if (user?.isSuperuser == true) {
                                    BadgeLabel(text = "SUPER ADMIN", containerColor = Primary.copy(alpha = 0.15f), contentColor = Primary, borderColor = Primary.copy(alpha = 0.3f))
                                } else {
                                    BadgeLabel(text = "ADMIN", containerColor = CyanAccent.copy(alpha = 0.15f), contentColor = CyanAccent, borderColor = CyanAccent.copy(alpha = 0.3f))
                                }

                                if (user?.isActive == true) {
                                    BadgeLabel(text = "ACTIVE", containerColor = UpGreen.copy(alpha = 0.15f), contentColor = UpGreen, borderColor = UpGreen.copy(alpha = 0.3f), hasIndicator = true)
                                }
                            }
                        }
                    }
                }
            }

            // 2. Account Details Table Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = SolidColor(BorderColor))
            ) {
                Column(modifier = Modifier.fillMaxWidth()) {
                    CardHeader(icon = Icons.Default.Fingerprint, title = "Account Details")

                    InfoRow(icon = Icons.Default.Person, label = "User ID", value = "#${user?.id ?: "—"}")
                    InfoRow(icon = Icons.Default.Mail, label = "Email Address", value = user?.email ?: "—")
                    InfoRow(icon = Icons.Default.Shield, label = "Permission Level", value = if (user?.isSuperuser == true) "Superuser (L2)" else "Administrator (L1)")
                    InfoRow(icon = Icons.Default.Computer, label = "Active Platform", value = "Android App")
                    
                    // Repaired Server Connection Row
                    val baseUrl = ApiClient.baseUrl
                    InfoRow(icon = Icons.Default.Dns, label = "Server Connection", value = baseUrl.ifBlank { "Not set" }, isLast = true)
                }
            }

            // 3. Update Profile Form Card
            var showForm by remember { mutableStateOf(false) }
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = SolidColor(BorderColor))
            ) {
                Column(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { showForm = !showForm }
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Edit, contentDescription = null, tint = Primary, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(10.dp))
                            Text("Update Profile Details", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        }
                        Icon(
                            imageVector = if (showForm) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                            contentDescription = null,
                            tint = Color.Gray
                        )
                    }

                    AnimatedVisibility(visible = showForm) {
                        Column(
                            modifier = Modifier.padding(start = 14.dp, end = 14.dp, bottom = 16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Divider(color = BorderColor)

                            OutlinedTextField(
                                value = nameInput,
                                onValueChange = { nameInput = it; updateSuccess = false; updateError = null },
                                label = { Text("Display Name") },
                                singleLine = true,
                                modifier = Modifier.fillMaxWidth(),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Primary,
                                    unfocusedBorderColor = BorderColor,
                                    focusedLabelColor = Primary,
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            OutlinedTextField(
                                value = emailInput,
                                onValueChange = { emailInput = it; updateSuccess = false; updateError = null },
                                label = { Text("Email Address") },
                                singleLine = true,
                                modifier = Modifier.fillMaxWidth(),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Primary,
                                    unfocusedBorderColor = BorderColor,
                                    focusedLabelColor = Primary,
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            OutlinedTextField(
                                value = passwordInput,
                                onValueChange = { passwordInput = it; updateSuccess = false; updateError = null },
                                label = { Text("New Password (leave blank to keep current)") },
                                visualTransformation = PasswordVisualTransformation(),
                                singleLine = true,
                                modifier = Modifier.fillMaxWidth(),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Primary,
                                    unfocusedBorderColor = BorderColor,
                                    focusedLabelColor = Primary,
                                    unfocusedLabelColor = Color.Gray,
                                    focusedTextColor = Color.White,
                                    unfocusedTextColor = Color.White
                                )
                            )

                            if (updateSuccess) {
                                Text("Profile updated successfully.", color = UpGreen, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                            }

                            if (updateError != null) {
                                Text(updateError!!, color = DownRed, fontSize = 12.sp, fontWeight = FontWeight.Medium)
                            }

                            Button(
                                onClick = {
                                    scope.launch {
                                        isUpdating = true
                                        updateSuccess = false
                                        updateError = null
                                        try {
                                            val service = ApiClient.getService()
                                            val updatedRes = service.updateMe(
                                                UserUpdate(
                                                    email = emailInput.takeIf { it.isNotBlank() && it != user?.email },
                                                    fullName = nameInput.takeIf { it.isNotBlank() && it != user?.fullName },
                                                    password = passwordInput.takeIf { it.isNotBlank() }
                                                )
                                            )
                                            val updatedUser = updatedRes.data
                                            user = updatedUser
                                            prefManager.userEmail = updatedUser.email
                                            passwordInput = ""
                                            updateSuccess = true
                                        } catch (e: Exception) {
                                            updateError = e.toApiErrorMessage()
                                        } finally {
                                            isUpdating = false
                                        }
                                    }
                                },
                                modifier = Modifier.fillMaxWidth().height(48.dp),
                                shape = RoundedCornerShape(10.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = Primary),
                                enabled = !isUpdating
                            ) {
                                if (isUpdating) {
                                    CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp))
                                } else {
                                    Text("Save Changes", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }

            // 4. Session Token Card
            val activeToken = prefManager.authToken ?: ""
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = SolidColor(BorderColor))
            ) {
                Column(modifier = Modifier.fillMaxWidth().padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Key, contentDescription = null, tint = Primary, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(10.dp))
                            Text("Active Session Token", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        }

                        BadgeLabel(text = "LIVE", containerColor = UpGreen.copy(alpha = 0.15f), contentColor = UpGreen, borderColor = UpGreen.copy(alpha = 0.3f))
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF060910), shape = RoundedCornerShape(10.dp))
                            .border(1.dp, BorderColor, shape = RoundedCornerShape(10.dp))
                            .padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = if (activeToken.length > 30) "${activeToken.take(30)}..." else activeToken.ifEmpty { "No Active Token" },
                            color = Color.Gray,
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace,
                            modifier = Modifier.weight(1f)
                        )

                        IconButton(
                            onClick = {
                                if (activeToken.isNotEmpty()) {
                                    clipboardManager.setText(AnnotatedString(activeToken))
                                    tokenCopied = true
                                }
                            },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = if (tokenCopied) Icons.Default.CheckCircle else Icons.Default.ContentCopy,
                                contentDescription = "Copy Token",
                                tint = if (tokenCopied) UpGreen else Primary,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }

                    if (tokenCopied) {
                        LaunchedEffect(Unit) {
                            kotlinx.coroutines.delay(2000)
                            tokenCopied = false
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "JWT Bearer token - used for all API requests. Do not share this with anyone. Expires on logout.",
                        color = Color.DarkGray,
                        fontSize = 10.sp
                    )
                }
            }

            // 5. Danger Zone / Logout
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = DownRed.copy(alpha = 0.03f)),
                border = CardDefaults.outlinedCardBorder().copy(width = 1.dp, brush = SolidColor(DownRed.copy(alpha = 0.15f)))
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Session Control", color = DownRed, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        Text(
                            text = "Revoke your current JWT token and sign out from this device.",
                            color = Color.Gray,
                            fontSize = 11.sp,
                            modifier = Modifier.padding(top = 2.dp)
                        )
                    }

                    Button(
                        onClick = {
                            prefManager.clear()
                            onLogout()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = DownRed),
                        shape = RoundedCornerShape(10.dp),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Default.ExitToApp, contentDescription = null, tint = Color.White, modifier = Modifier.size(16.dp))
                            Text("Sign Out", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}
// ... (BadgeLabel, CardHeader, InfoRow remain the same)
@Composable
fun BadgeLabel(
    text: String,
    containerColor: Color,
    contentColor: Color,
    borderColor: Color,
    hasIndicator: Boolean = false
) {
    Box(
        modifier = Modifier
            .background(containerColor, shape = RoundedCornerShape(6.dp))
            .border(1.dp, borderColor, shape = RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            if (hasIndicator) {
                Box(
                    modifier = Modifier
                        .size(6.dp)
                        .background(contentColor, shape = CircleShape)
                )
            }
            Text(
                text = text,
                color = contentColor,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun CardHeader(icon: ImageVector, title: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = null, tint = Primary, modifier = Modifier.size(18.dp))
        Spacer(modifier = Modifier.width(10.dp))
        Text(title, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
    }
    Divider(color = BorderColor)
}

@Composable
fun InfoRow(
    icon: ImageVector,
    label: String,
    value: String,
    isLast: Boolean = false
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .background(Primary.copy(alpha = 0.1f), shape = RoundedCornerShape(6.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = Primary, modifier = Modifier.size(14.dp))
            }
            Spacer(modifier = Modifier.width(10.dp))
            Text(label, color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.Medium)
        }
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = value,
            color = TextPrimary,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            textAlign = TextAlign.End,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f)
        )
    }
    if (!isLast) {
        Divider(color = BorderColor.copy(alpha = 0.5f), modifier = Modifier.padding(horizontal = 14.dp))
    }
}
