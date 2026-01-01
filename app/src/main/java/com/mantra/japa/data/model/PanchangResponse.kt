package com.mantra.japa.data.model

data class PanchangResponse(
    val tithi: Tithi
)

data class Tithi(
    val details: TithiDetails,
    val end_time: String,
    val end_time_ms: Long
)

data class TithiDetails(
    val tithi_number: Int,
    val tithi_name: String,
    val special: String,
    val summary: String,
    val deity: String
)
