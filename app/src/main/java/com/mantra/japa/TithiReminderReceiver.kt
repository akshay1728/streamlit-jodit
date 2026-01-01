package com.mantra.japa

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.mantra.japa.data.model.PanchangResponse
import com.mantra.japa.data.network.PanchangRequest
import com.mantra.japa.data.network.RetrofitInstance
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.Calendar
import java.util.TimeZone

class TithiReminderReceiver : BroadcastReceiver() {

    private val coroutineScope = CoroutineScope(Dispatchers.IO)

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            TithiReminderScheduler.scheduleDailyReminder(context)
            return
        }

        val pendingResult = goAsync()
        coroutineScope.launch {
            try {
                val sharedPreferences = context.getSharedPreferences("tithi_prefs", Context.MODE_PRIVATE)
                val lat = sharedPreferences.getString("lat", "19.0760")?.toDouble() ?: 19.0760
                val lon = sharedPreferences.getString("lon", "72.8777")?.toDouble() ?: 72.8777
                val tzone = sharedPreferences.getString("tzone", TimeZone.getDefault().id) ?: TimeZone.getDefault().id

                val calendar = Calendar.getInstance()
                val request = PanchangRequest(
                    day = calendar.get(Calendar.DAY_OF_MONTH),
                    month = calendar.get(Calendar.MONTH) + 1,
                    year = calendar.get(Calendar.YEAR),
                    lat = lat,
                    lon = lon,
                    tzone = tzone
                )
                val response = RetrofitInstance.api.getPanchang("Basic " + BuildConfig.API_KEY, request)
                showNotification(context, response)
            } catch (e: Exception) {
                Log.e("TithiReminderReceiver", "Error fetching Tithi", e)
            } finally {
                pendingResult.finish()
            }
        }
    }

    private fun showNotification(context: Context, panchangResponse: PanchangResponse) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "tithi_reminder_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Tithi Reminders",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(context, channelId)
            .setContentTitle(context.getString(R.string.todays_tithi))
            .setContentText(context.getString(R.string.today_is, panchangResponse.tithi.details.tithi_name))
            .setSmallIcon(R.drawable.ic_notification)
            .build()

        notificationManager.notify(1, notification)
    }
}
