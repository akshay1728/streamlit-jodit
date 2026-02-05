package com.mantra.japa.utils

import android.content.Context
import com.itextpdf.kernel.pdf.PdfDocument
import com.itextpdf.kernel.pdf.PdfWriter
import com.itextpdf.kernel.colors.ColorConstants
import com.itextpdf.layout.Document
import com.itextpdf.layout.element.Cell
import com.itextpdf.layout.element.Paragraph
import com.itextpdf.layout.element.Table
import com.itextpdf.layout.property.TextAlignment
import com.itextpdf.layout.property.UnitValue
import com.mantra.japa.ui.viewmodel.DeityStatistics
import com.mantra.japa.ui.viewmodel.NoteDetails
import com.mantra.japa.ui.viewmodel.Statistics
import android.content.ContentValues
import android.provider.MediaStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.OutputStream

class PdfExporter {
    suspend fun exportToPdf(
        context: Context,
        statistics: List<Statistics>,
        deityStatistics: List<DeityStatistics>,
        notes: List<NoteDetails>
    ) = withContext(Dispatchers.IO) {
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, "Japa_Report.pdf")
            put(MediaStore.MediaColumns.MIME_TYPE, "application/pdf")
            put(MediaStore.MediaColumns.RELATIVE_PATH, "Download/MantraJapa")
        }

        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Files.getContentUri("external"), contentValues)

        if (uri != null) {
            resolver.openOutputStream(uri)?.use { outputStream ->
                val writer = PdfWriter(outputStream)
                val pdf = PdfDocument(writer)
                val document = Document(pdf)

                // Title
                document.add(Paragraph("Japa Report")
                    .setTextAlignment(TextAlignment.CENTER)
                    .setBold()
                    .setFontSize(24f)
                    .setFontColor(ColorConstants.BLUE))

                // Mantra Statistics
                document.add(Paragraph("Mantra Statistics")
                    .setBold()
                    .setFontSize(18f)
                    .setMarginTop(20f))

                val mantraTable = Table(UnitValue.createPercentArray(floatArrayOf(3f, 2f, 1f, 1f))).useAllAvailableWidth()
                mantraTable.addHeaderCell(createHeaderCell("Mantra"))
                mantraTable.addHeaderCell(createHeaderCell("Deity"))
                mantraTable.addHeaderCell(createHeaderCell("Total Malas"))
                mantraTable.addHeaderCell(createHeaderCell("Total Japas"))

                statistics.forEach {
                    mantraTable.addCell(it.mantra.name)
                    mantraTable.addCell(it.deity.name)
                    mantraTable.addCell(it.totalMalas.toString())
                    mantraTable.addCell(it.totalJapas.toString())
                }
                document.add(mantraTable)

                // Deity Statistics
                document.add(Paragraph("Deity Statistics")
                    .setBold()
                    .setFontSize(18f)
                    .setMarginTop(20f))

                val deityTable = Table(UnitValue.createPercentArray(floatArrayOf(3f, 1f, 1f))).useAllAvailableWidth()
                deityTable.addHeaderCell(createHeaderCell("Deity"))
                deityTable.addHeaderCell(createHeaderCell("Total Malas"))
                deityTable.addHeaderCell(createHeaderCell("Total Japas"))

                deityStatistics.forEach {
                    deityTable.addCell(it.deity.name)
                    deityTable.addCell(it.totalMalas.toString())
                    deityTable.addCell(it.totalJapas.toString())
                }
                document.add(deityTable)

                // Notes
                document.add(Paragraph("Notes")
                    .setBold()
                    .setFontSize(18f)
                    .setMarginTop(20f))

                notes.forEach {
                    document.add(Paragraph("${it.mantra.name}:")
                        .setBold())
                    document.add(Paragraph(it.note.text)
                        .setMarginLeft(20f))
                }

                document.close()
            }
        }
    }

    private fun createHeaderCell(text: String): Cell {
        return Cell().add(Paragraph(text)
            .setBold()
            .setFontColor(ColorConstants.WHITE)
            .setBackgroundColor(ColorConstants.BLUE)
            .setTextAlignment(TextAlignment.CENTER))
    }
}
