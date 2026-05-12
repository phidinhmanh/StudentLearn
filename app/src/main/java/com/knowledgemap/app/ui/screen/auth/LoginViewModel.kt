package com.knowledgemap.app.ui.screen.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.data.remote.StudentLearnApi
import com.knowledgemap.app.data.remote.dto.UserLoginRequest
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: String? = null,
    val isSuccess: Boolean = false
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val api: StudentLearnApi
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun onEmailChange(email: String) {
        _uiState.value = _uiState.value.copy(email = email, error = null)
    }

    fun onPasswordChange(password: String) {
        _uiState.value = _uiState.value.copy(password = password, error = null)
    }

    fun login(onSuccess: () -> Unit) {
        val state = _uiState.value
        if (state.email.isBlank() || state.password.isBlank()) {
            _uiState.value = state.copy(error = "Vui lòng nhập đầy đủ thông tin")
            return
        }

        viewModelScope.launch {
            _uiState.value = state.copy(isLoading = true, error = null)
            try {
                val response = api.login(UserLoginRequest(state.email, state.password))
                if (response.isSuccessful) {
                    val token = response.body()?.access_token
                    if (token != null) {
                        // Token saved via AuthInterceptor SharedPreferences
                        _uiState.value = _uiState.value.copy(isLoading = false, isSuccess = true)
                        onSuccess()
                    } else {
                        _uiState.value = _uiState.value.copy(isLoading = false, error = "Đăng nhập thất bại")
                    }
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = when (response.code()) {
                            401 -> "Sai email hoặc mật khẩu"
                            else -> "Đăng nhập thất bại"
                        }
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "Không thể kết nối server"
                )
            }
        }
    }
}