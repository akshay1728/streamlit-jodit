package com.mantra.japa.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mantra.japa.data.dao.DeityDao
import com.mantra.japa.data.dao.JapaEntryDao
import com.mantra.japa.data.dao.MantraDao
import com.mantra.japa.data.dao.NoteDao
import com.mantra.japa.data.model.Deity
import com.mantra.japa.data.model.DeityStatistics
import com.mantra.japa.data.model.JapaEntry
import com.mantra.japa.data.model.Mantra
import com.mantra.japa.data.model.Note
import com.mantra.japa.data.model.Statistics
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.util.Calendar
import java.util.Date

class MainViewModel(
    private val mantraDao: MantraDao,
    private val deityDao: DeityDao,
    private val japaEntryDao: JapaEntryDao,
    private val noteDao: NoteDao
) : ViewModel() {

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

    fun getStatisticsForMantra(mantraId: Long) = combine(
        japaEntryDao.getJapaEntriesForMantra(mantraId),
        mantraDao.getAllMantras(),
        deityDao.getAllDeities()
    ) { japaEntries, mantras, deities ->
        val mantra = mantras.find { it.id == mantraId }
        val deity = deities.find { it.id == mantra?.deityId }
        val totalMalas = japaEntries.sumOf { it.malas }
        val totalJapas = totalMalas * 108
        if (mantra != null && deity != null) {
            Statistics(mantra, deity, totalMalas, totalJapas)
        } else {
            null
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

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

    fun addNote(mantraId: Long, text: String) {
        viewModelScope.launch {
            noteDao.insert(Note(mantraId = mantraId, text = text, timestamp = Date()))
        }
    }

    private val _notesFilter = MutableStateFlow("")
    val notesFilter = _notesFilter

    private val _selectedYear = MutableStateFlow<Int?>(null)
    val selectedYear = _selectedYear

    private val _selectedMonth = MutableStateFlow<Int?>(null)
    val selectedMonth = _selectedMonth

    val notes = combine(
        noteDao.getAllNotes(),
        mantras,
        deities,
        _notesFilter,
        _selectedYear,
        _selectedMonth
    ) { notes, mantras, deities, filter, year, month ->
        val calendar = Calendar.getInstance()
        notes.mapNotNull { note ->
            val mantra = mantras.find { it.id == note.mantraId }
            val deity = deities.find { it.id == mantra?.deityId }
            if (mantra != null && deity != null) {
                NoteDetails(note, mantra, deity)
            } else {
                null
            }
        }.filter { noteDetails ->
            val textFilterPassed = filter.isBlank() ||
                    noteDetails.mantra.name.contains(filter, ignoreCase = true) ||
                    noteDetails.deity.name.contains(filter, ignoreCase = true) ||
                    noteDetails.note.text.contains(filter, ignoreCase = true)

            calendar.time = noteDetails.note.timestamp
            val noteYear = calendar.get(Calendar.YEAR)
            val noteMonth = calendar.get(Calendar.MONTH) + 1 // Calendar months are 0-indexed

            val yearFilterPassed = year == null || noteYear == year
            val monthFilterPassed = month == null || noteMonth == month

            textFilterPassed && yearFilterPassed && monthFilterPassed
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun onNotesFilterChanged(newFilter: String) {
        _notesFilter.value = newFilter
    }

    fun onYearSelected(year: Int?) {
        _selectedYear.value = year
    }

    fun onMonthSelected(month: Int?) {
        _selectedMonth.value = month
    }
}

data class NoteDetails(
    val note: Note,
    val mantra: Mantra,
    val deity: Deity
)
