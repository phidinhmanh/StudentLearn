package com.knowledgemap.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class KnowledgeMapApplication : Application() {

    override fun onCreate() {
        super.onCreate()
    }
}