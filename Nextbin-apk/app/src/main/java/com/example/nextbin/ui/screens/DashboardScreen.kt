package com.example.nextbin.ui.screens

import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Article
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.PrefManager
import com.example.nextbin.theme.Background
import com.example.nextbin.theme.DownRed
import com.example.nextbin.theme.Primary
import com.example.nextbin.theme.SurfaceCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onLogout: () -> Unit
) {
    var selectedTab by remember { mutableIntStateOf(0) }
    var showLogsScreen by remember { mutableStateOf(false) }
    var showProfile by remember { mutableStateOf(false) }
    var isSidebarExpanded by remember { mutableStateOf(true) }
    
    val context = LocalContext.current
    val prefManager = remember { PrefManager(context) }
    var refreshTrigger by remember { mutableIntStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { isSidebarExpanded = !isSidebarExpanded }) {
                            Icon(Icons.Default.Menu, contentDescription = "Toggle Sidebar", tint = Color.White)
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (showProfile) "Profile" else "Nextbin.in Control",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Black,
                            color = Color.White
                        )
                    }
                },
                actions = {
                    if (!showProfile) {
                        IconButton(onClick = { refreshTrigger++ }) {
                            Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = Color.White)
                        }
                    }
                    IconButton(onClick = { showProfile = !showProfile }) {
                        Icon(
                            imageVector = if (showProfile) Icons.Default.Close else Icons.Default.Person,
                            contentDescription = if (showProfile) "Close Profile" else "Profile",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceCard, titleContentColor = Color.White),
                modifier = Modifier.height(64.dp)
            )
        },
        bottomBar = {
            if (!showProfile && !showLogsScreen) {
                NavigationBar(containerColor = SurfaceCard, modifier = Modifier.height(72.dp)) {
                    val tabs = listOf(
                        Triple(0, "Overview", Icons.Default.Dashboard),
                        Triple(1, "Monitors", Icons.Default.Assessment),
                        Triple(2, "Instagram", Icons.Default.Forum),
                        Triple(3, "Audit", Icons.Default.Shield)
                    )
                    tabs.forEach { (index, label, icon) ->
                        NavigationBarItem(
                            selected = selectedTab == index,
                            onClick = { selectedTab = index; showLogsScreen = false },
                            icon = { Icon(icon, contentDescription = label) },
                            label = { Text(label, fontSize = 10.sp) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = Primary,
                                selectedTextColor = Color.White,
                                unselectedIconColor = Color.Gray,
                                unselectedTextColor = Color.Gray,
                                indicatorColor = SurfaceCard
                            )
                        )
                    }
                }
            }
        },
        containerColor = Background
    ) { paddingValues ->
        Row(modifier = Modifier.fillMaxSize().padding(paddingValues)) {
            // Sidebar
            Column(
                modifier = Modifier
                    .fillMaxHeight()
                    .animateContentSize(animationSpec = tween(300))
                    .width(if (isSidebarExpanded) 200.dp else 0.dp)
                    .background(SurfaceCard)
                    .padding(vertical = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                if (isSidebarExpanded) {
                    SidebarItem(
                        icon = Icons.AutoMirrored.Filled.Article,
                        label = "Logs",
                        isExpanded = true,
                        selected = showLogsScreen,
                        onClick = { showLogsScreen = true; selectedTab = -1 }
                    )
                    Spacer(modifier = Modifier.weight(1f))
                    
                    // Logout button in sidebar
                    TextButton(
                        onClick = {
                            prefManager.clear()
                            onLogout()
                        },
                        modifier = Modifier
                            .padding(16.dp)
                            .fillMaxWidth()
                    ) {
                        Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Logout", tint = DownRed)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Sign Out", color = DownRed, fontWeight = FontWeight.Bold)
                    }
                }
            }
            
            // Main Content
            Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                if (showProfile) {
                    ProfileTab(refreshTrigger = refreshTrigger, onLogout = onLogout)
                } else if (showLogsScreen) {
                    LogsScreen()
                } else {
                    when (selectedTab) {
                        0 -> DashboardOverviewTab(refreshTrigger, onViewAllAuditLogs = { selectedTab = 3 })
                        1 -> MonitorsTab(refreshTrigger)
                        2 -> InstagramTab(refreshTrigger)
                        3 -> AuditLogsTab(refreshTrigger)
                    }
                }
            }
        }
    }
}

@Composable
fun SidebarItem(icon: ImageVector, label: String, isExpanded: Boolean, selected: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .padding(horizontal = 8.dp, vertical = 4.dp)
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (selected) Primary.copy(alpha = 0.2f) else Color.Transparent)
            .clickable { onClick() }
            .padding(12.dp),
        contentAlignment = Alignment.CenterStart
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, contentDescription = label, tint = if (selected) Primary else Color.Gray)
            if (isExpanded) {
                Spacer(modifier = Modifier.width(16.dp))
                Text(label, color = if (selected) Primary else Color.Gray, fontWeight = FontWeight.Bold)
            }
        }
    }
}
