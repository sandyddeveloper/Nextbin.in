package com.example.nextbin.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.nextbin.data.PrefManager
import com.example.nextbin.theme.Background
import com.example.nextbin.theme.BorderColor
import com.example.nextbin.theme.Primary
import com.example.nextbin.theme.SurfaceCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onLogout: () -> Unit
) {
    var selectedTab by remember { mutableStateOf(0) }
    var showProfile by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val prefManager = remember { PrefManager(context) }
    
    // Refresh triggers to propagate down to child tabs
    var refreshTrigger by remember { mutableStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = if (showProfile) "Profile" else "Nextbin.in Control",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Black,
                            color = Color.White
                        )
                        if (!showProfile) {
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Live monitoring, security events, and Instagram agents at a glance",
                                fontSize = 12.sp,
                                color = Color.LightGray,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                },
                actions = {
                    if (!showProfile) {
                        IconButton(onClick = { refreshTrigger++ }) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Refresh",
                                tint = Color.White
                            )
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
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = SurfaceCard,
                    titleContentColor = Color.White
                ),
                modifier = Modifier.height(88.dp)
            )
        },
        bottomBar = {
            if (!showProfile) {
                NavigationBar(
                    containerColor = SurfaceCard,
                    tonalElevation = 8.dp,
                    modifier = Modifier.height(72.dp)
                ) {
                    NavigationBarItem(
                        selected = selectedTab == 0,
                        onClick = { selectedTab = 0 },
                        icon = { Icon(Icons.Default.Dashboard, contentDescription = "Overview") },
                        label = { Text("Overview", fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Primary,
                            selectedTextColor = Color.White,
                            unselectedIconColor = Color.Gray,
                            unselectedTextColor = Color.Gray,
                            indicatorColor = SurfaceCard
                        )
                    )
                    NavigationBarItem(
                        selected = selectedTab == 1,
                        onClick = { selectedTab = 1 },
                        icon = { Icon(Icons.Default.Assessment, contentDescription = "Monitors") },
                        label = { Text("Monitors", fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Primary,
                            selectedTextColor = Color.White,
                            unselectedIconColor = Color.Gray,
                            unselectedTextColor = Color.Gray,
                            indicatorColor = SurfaceCard
                        )
                    )
                    NavigationBarItem(
                        selected = selectedTab == 2,
                        onClick = { selectedTab = 2 },
                        icon = { Icon(Icons.Default.Forum, contentDescription = "Instagram") },
                        label = { Text("Instagram", fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Primary,
                            selectedTextColor = Color.White,
                            unselectedIconColor = Color.Gray,
                            unselectedTextColor = Color.Gray,
                            indicatorColor = SurfaceCard
                        )
                    )
                    NavigationBarItem(
                        selected = selectedTab == 3,
                        onClick = { selectedTab = 3 },
                        icon = { Icon(Icons.Default.Shield, contentDescription = "Audit") },
                        label = { Text("Audit Stream", fontSize = 11.sp) },
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
        },
        containerColor = Background
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Background)
        ) {
            if (showProfile) {
                ProfileTab(refreshTrigger = refreshTrigger, onLogout = onLogout)
            } else {
                when (selectedTab) {
                    0 -> DashboardOverviewTab(
                        refreshTrigger = refreshTrigger,
                        onViewAllAuditLogs = { selectedTab = 3 }
                    )
                    1 -> MonitorsTab(refreshTrigger = refreshTrigger)
                    2 -> InstagramTab(refreshTrigger = refreshTrigger)
                    3 -> AuditLogsTab(refreshTrigger = refreshTrigger)
                }
            }
        }
    }
}
