package com.example.nextbin

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import com.example.nextbin.data.PrefManager
import com.example.nextbin.data.api.ApiClient
import com.example.nextbin.ui.screens.DashboardScreen
import com.example.nextbin.ui.screens.LoginScreen
import com.example.nextbin.ui.screens.ServerSetupScreen

@Composable
fun MainNavigation() {
  val context = LocalContext.current
  val prefManager = remember { PrefManager(context) }

  // Dynamic initial route resolution on app startup
  val initialRoute = remember {
    val savedUrl = prefManager.serverUrl
    val savedToken = prefManager.authToken
    
    if (savedUrl.isNullOrEmpty()) {
      ServerSetup
    } else {
      ApiClient.baseUrl = savedUrl
      if (savedToken.isNullOrEmpty()) {
        Login
      } else {
        ApiClient.setAuthToken(savedToken)
        Dashboard
      }
    }
  }

  val backStack = rememberNavBackStack(initialRoute)

  NavDisplay(
    backStack = backStack,
    onBack = { backStack.removeLastOrNull() },
    entryProvider =
      entryProvider {
        entry<ServerSetup> {
          ServerSetupScreen(
            onConnectionSuccess = {
              backStack.add(Login)
            }
          )
        }
        
        entry<Login> {
          LoginScreen(
            onLoginSuccess = {
              backStack.add(Dashboard)
            },
            onNavigateBack = {
              prefManager.clearAll()
              backStack.add(ServerSetup)
            }
          )
        }
        
        entry<Dashboard> {
          DashboardScreen(
            onLogout = {
              backStack.add(Login)
            }
          )
        }
      },
  )
}
