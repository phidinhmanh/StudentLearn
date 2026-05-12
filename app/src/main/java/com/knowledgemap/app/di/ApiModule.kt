package com.knowledgemap.app.di

import com.knowledgemap.app.data.utils.TextChunker
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object ApiModule {

    @Provides
    @Singleton
    fun provideTextChunker(): TextChunker {
        return TextChunker()
    }
}