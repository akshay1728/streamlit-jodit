package com.mantra.japa.data.network

import com.mantra.japa.data.model.PanchangResponse
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

interface ApiService {
    @POST("v1/panchang")
    suspend fun getPanchang(
        @Header("Authorization") apiKey: String,
        @Body request: PanchangRequest
    ): PanchangResponse
}

data class PanchangRequest(
    val day: Int,
    val month: Int,
    val year: Int,
    val lat: Double,
    val lon: Double,
    val tzone: String
)
