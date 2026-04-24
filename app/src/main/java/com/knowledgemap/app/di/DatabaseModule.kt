package com.knowledgemap.app.di

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import com.knowledgemap.app.data.local.KnowledgeMapDatabase
import com.knowledgemap.app.data.local.dao.AssessmentHistoryDao
import com.knowledgemap.app.data.local.dao.SessionLogDao
import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    private const val TAG = "DatabaseModule"
    private const val PREFS_NAME = "knowledgemap_prefs"
    private const val KEY_SEEDED = "default_data_seeded"

    @Provides
    @Singleton
    fun provideSharedPreferences(
        @ApplicationContext context: Context
    ): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context,
        prefs: SharedPreferences
    ): KnowledgeMapDatabase {
        return Room.databaseBuilder(
            context,
            KnowledgeMapDatabase::class.java,
            KnowledgeMapDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .addCallback(object : RoomDatabase.Callback() {
                override fun onCreate(db: SupportSQLiteDatabase) {
                    super.onCreate(db)
                    Log.d(TAG, "Database created — seeding default data via SQL")
                    seedViaSql(db, context)
                    prefs.edit().putBoolean(KEY_SEEDED, true).apply()
                }

                override fun onOpen(db: SupportSQLiteDatabase) {
                    super.onOpen(db)
                    if (!prefs.getBoolean(KEY_SEEDED, false)) {
                        val cursor = db.query("SELECT COUNT(*) FROM topic_node WHERE subject = 'toan10'")
                        var count = 0
                        if (cursor.moveToFirst()) {
                            count = cursor.getInt(0)
                        }
                        cursor.close()
                        if (count == 0) {
                            Log.d(TAG, "DB empty on open — seeding default data")
                            seedViaSql(db, context)
                            prefs.edit().putBoolean(KEY_SEEDED, true).apply()
                        } else {
                            prefs.edit().putBoolean(KEY_SEEDED, true).apply()
                        }
                    }
                }
            })
            .build()
    }

    private fun seedViaSql(db: SupportSQLiteDatabase, context: Context) {
        try {
            val json = context.assets.open("toan10_graph.json")
                .bufferedReader().use { it.readText() }
            val root = JSONObject(json)

            val nodesArray = root.getJSONArray("nodes")
            for (i in 0 until nodesArray.length()) {
                val obj = nodesArray.getJSONObject(i)
                val lastAssessed = if (obj.has("last_assessed") && !obj.isNull("last_assessed"))
                    obj.getLong("last_assessed").toString() else "NULL"

                db.execSQL(
                    """INSERT OR IGNORE INTO topic_node
                       (id, name, desc, difficulty, chapter, subject, skill_level, last_assessed)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    arrayOf(
                        obj.getString("id"),
                        obj.getString("name"),
                        obj.getString("desc"),
                        obj.getInt("difficulty").toString(),
                        obj.getString("chapter"),
                        obj.optString("subject", "toan10"),
                        obj.optInt("skill_level", 0).toString(),
                        if (lastAssessed == "NULL") null else lastAssessed
                    )
                )
            }

            val edgesArray = root.getJSONArray("edges")
            for (i in 0 until edgesArray.length()) {
                val obj = edgesArray.getJSONObject(i)
                db.execSQL(
                    """INSERT OR IGNORE INTO topic_edge
                       (from_id, to_id, relation, weight)
                       VALUES (?, ?, ?, ?)""",
                    arrayOf(
                        obj.getString("from_id"),
                        obj.getString("to_id"),
                        obj.getString("relation"),
                        obj.optDouble("weight", 1.0).toString()
                    )
                )
            }

            Log.d(TAG, "Seeded ${nodesArray.length()} nodes, ${edgesArray.length()} edges via SQL")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to seed default data", e)
        }
    }

    @Provides
    @Singleton
    fun provideTopicNodeDao(database: KnowledgeMapDatabase): TopicNodeDao {
        return database.topicNodeDao()
    }

    @Provides
    @Singleton
    fun provideTopicEdgeDao(database: KnowledgeMapDatabase): TopicEdgeDao {
        return database.topicEdgeDao()
    }

    @Provides
    @Singleton
    fun provideAssessmentHistoryDao(database: KnowledgeMapDatabase): AssessmentHistoryDao {
        return database.assessmentHistoryDao()
    }

    @Provides
    @Singleton
    fun provideSessionLogDao(database: KnowledgeMapDatabase): SessionLogDao {
        return database.sessionLogDao()
    }
}
