package com.knowledgemap.app.di

import android.content.Context
import com.knowledgemap.app.data.remote.GeminiGraphExtractor
import com.knowledgemap.app.data.remote.GeminiQuizGenerator
import com.knowledgemap.app.data.utils.GraphValidator
import com.knowledgemap.app.data.utils.QuizParser
import com.knowledgemap.app.data.utils.TextChunker
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
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

    @Provides
    @Singleton
    fun provideGraphValidator(): GraphValidator {
        return GraphValidator()
    }

    @Provides
    @Singleton
    fun provideQuizParser(): QuizParser {
        return QuizParser()
    }

    @Provides
    @Singleton
    fun provideGeminiGraphExtractor(
        @ApplicationContext context: Context,
        validator: GraphValidator
    ): GeminiGraphExtractor {
        return GeminiGraphExtractor(context, validator)
    }

    @Provides
    @Singleton
    fun provideGeminiQuizGenerator(
        @ApplicationContext context: Context,
        quizParser: QuizParser
    ): GeminiQuizGenerator {
        return GeminiQuizGenerator(context, quizParser)
    }
}