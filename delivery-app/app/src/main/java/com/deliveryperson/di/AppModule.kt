package com.deliveryperson.di

import android.content.Context
import com.deliveryperson.data.repository.DeliveryRepository
import com.deliveryperson.network.ApiService
import com.deliveryperson.network.RetrofitClient
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return RetrofitClient.apiService
    }

    @Provides
    @Singleton
    fun provideDeliveryRepository(apiService: ApiService): DeliveryRepository {
        return DeliveryRepository(apiService)
    }
}
