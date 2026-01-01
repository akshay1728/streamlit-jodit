package com.mantra.japa.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mantra.japa.BuildConfig
import com.mantra.japa.data.dao.DeityDao
import com.mantra.japa.data.dao.JapaEntryDao
import com.mantra.japa.data.dao.MantraDao
import com.mantra.japa.data.dao.TargetDao
import com.mantra.japa.data.model.Deity
import com.mantra.japa.data.model.DeityStatistics
import com.mantra.japa.data.model.JapaEntry
import com.mantra.japa.data.model.Mantra
import com.mantra.japa.data.model.PanchangResponse
import com.mantra.japa.data.model.Statistics
import com.mantra.japa.data.model.Target
import com.mantra.japa.data.network.PanchangRequest
import com.mantra.japa.data.network.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.util.Calendar
import java.util.Date
import java.util.TimeZone

class MainViewModel(
    private val mantraDao: MantraDao,
    private val deityDao: DeityDao,
    private val japaEntryDao: JapaEntryDao,
    private val targetDao: TargetDao
) : ViewModel() {

    private val _panchangResponse = MutableStateFlow<PanchangResponse?>(null)
    val panchangResponse: StateFlow<PanchangResponse?> = _panchangResponse.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    val mantras = mantraDao.getAllMantras()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val deities = deityDao.getAllDeities()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val statistics = combine(
        mantraDao.getAllMantras(),
        deityDao.getAllDeities(),
        japaEntryDao.getAllJapaEntries()
    ) { mantras, deities, japaEntries ->
        mantras.mapNotNull { mantra ->
            val deity = deities.find { it.id == mantra.deityId }
            if (deity != null) {
                val japaEntriesForMantra = japaEntries.filter { it.mantraId == mantra.id }
                val totalMalas = japaEntriesForMantra.sumOf { it.malas }
                val totalJapas = totalMalas * 108
                Statistics(mantra, deity, totalMalas, totalJapas)
            } else {
                null
            }
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val deityStatistics = combine(
        deityDao.getAllDeities(),
        mantraDao.getAllMantras(),
        japaEntryDao.getAllJapaEntries()
    ) { deities, mantras, japaEntries ->
        deities.map { deity ->
            val mantrasForDeity = mantras.filter { it.deityId == deity.id }
            val totalMalas = mantrasForDeity.sumOf { mantra ->
                japaEntries.filter { it.mantraId == mantra.id }.sumOf { it.malas }
            }
            val totalJapas = totalMalas * 108
            DeityStatistics(deity, totalMalas, totalJapas)
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun getTargetForMantra(mantraId: Long) = targetDao.getTargetForMantra(mantraId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

    fun addMantra(name: String, deityId: Long) {
        viewModelScope.launch {
            mantraDao.insert(Mantra(name = name, deityId = deityId))
        }
    }

    fun addDeity(name: String) {
        viewModelScope.launch {
            deityDao.insert(Deity(name = name))
        }
    }

    fun addJapaEntry(mantraId: Long, malas: Int) {
        viewModelScope.launch {
            japaEntryDao.insert(JapaEntry(mantraId = mantraId, malas = malas, timestamp = Date()))
        }
    }

    fun setTarget(mantraId: Long, targetMalas: Int, targetDate: Date) {
        viewModelScope.launch {
            targetDao.insert(Target(mantraId = mantraId, targetMalas = targetMalas, targetDate = targetDate))
        }
    }

    fun fetchPanchang(lat: Double = 19.0760, lon: Double = 72.8777, tzone: String = TimeZone.getDefault().id) {
        viewModelScope.launch {
            try {
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
                _panchangResponse.value = response
                _error.value = null
            } catch (e: Exception) {
                _error.value = "Error fetching Tithi: ${e.message}"
            }
        }
    }
}
