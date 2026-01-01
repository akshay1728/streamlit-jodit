package com.mantra.japa.utils

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

fun formatDate(date: Date): String {
    val format = SimpleDateFormat("MM/dd/yyyy", Locale.getDefault())
    return format.format(date)
}
