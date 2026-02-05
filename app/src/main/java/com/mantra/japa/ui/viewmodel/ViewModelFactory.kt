package com.mantra.japa.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.mantra.japa.data.dao.DeityDao
import com.mantra.japa.data.dao.JapaEntryDao
import com.mantra.japa.data.dao.MantraDao
import com.mantra.japa.data.dao.NoteDao

class ViewModelFactory(
    private val mantraDao: MantraDao,
    private val deityDao: DeityDao,
    private val japaEntryDao: JapaEntryDao,
    private val noteDao: NoteDao
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(mantraDao, deityDao, japaEntryDao, noteDao) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
