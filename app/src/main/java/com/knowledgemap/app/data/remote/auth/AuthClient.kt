package com.knowledgemap.app.data.remote.auth

import android.content.SharedPreferences
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor(
    private val prefs: SharedPreferences
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = prefs.getString(KEY_TOKEN, null)
        val request = if (token != null) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        return chain.proceed(request)
    }

    companion object {
        const val KEY_TOKEN = "auth_token"
    }
}

class TokenManager(
    private val prefs: SharedPreferences
) {
    fun saveToken(token: String) = prefs.edit().putString(AuthInterceptor.KEY_TOKEN, token).apply()
    fun getToken(): String? = prefs.getString(AuthInterceptor.KEY_TOKEN, null)
    fun clearToken() = prefs.edit().remove(AuthInterceptor.KEY_TOKEN).remove(KEY_USER_ID).apply()
    fun saveUserId(userId: String) = prefs.edit().putString(KEY_USER_ID, userId).apply()
    fun getUserId(): String? = prefs.getString(KEY_USER_ID, null)

    companion object {
        const val KEY_USER_ID = "user_id"
    }
}