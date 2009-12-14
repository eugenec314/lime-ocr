#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Version: 2.4
# Sub Version: 2.0
# SVN: r6
# Tue 12/15/2009 5:14:23.48 AM
##############   lime-ocr.py - version 2.4.2.0   ##############################
# Lime OCR, Free Opensource OCR Software with tesseract-ocr engine
#
# lime-ocr.py
# Copyright 2009 Nishad TR <nishad at limeconsultants.com>
# http://www.limeconsultants.com/
#
# tesseract-gui.py
# Copyright 2009 Juan Ramon Castan <juanramoncastan at yahoo.es>
# Based in the previous work of Filip Domenic "guitesseract.py" 
#
# guitesseract.py
# Copyright 2008 Filip Dominec <filip.dominec at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.#}}}


import pygtk
pygtk.require('2.0')
import gtk
import os
import pango
import sys
import subprocess
import string

class Whc:
	def __init__(self):
		# Lime OCR Hacks
		runBash2("splash.exe 3")
		runBash("ls.exe -m -1 tessdata\*.traineddata > lslang.txt")
		runBash("langlist.exe")
		runBash2("GUP.exe")
		# Enough
		
		###---Window and framework -----------------------------
		self.mainwindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.mainwindow.connect("destroy", self.destroy)
		
		self.mainwindow.set_title("Lime OCR 2.4.2")
		self.mainwindow.connect('destroy', lambda w: gtk.main_quit())
		self.mainwindow.set_icon_from_file("share\\lime-ocr\\lime-ocr-icon.png")

		self.f_fronend_lang()

		self.vboxWindow = gtk.VBox(False, 1)
		self.mainwindow.add(self.vboxWindow)
		self.vboxWindow.show()

		self.hboxWindow = gtk.HBox(False, 3)
		self.vboxWindow.pack_start(self.hboxWindow,True, True, 1)
		self.hboxWindow.show()
		#---------------------------------------------------

	###---Left of Window-------------------------------------
		self.vboxLeft = gtk.VBox(False, 1)
		self.hboxWindow.pack_start(self.vboxLeft, False, True, 2)
		self.vboxLeft.show()
		

		self.headHBox = gtk.HBox(False,1)
		self.vboxLeft.pack_start(self.headHBox, False, False, 1)
		self.headHBox.show()

		self.imgIcon=gtk.Image()
		self.imgIcon.set_from_file("share\\lime-ocr\\lime-ocr-logo-lime.png")
		self.headHBox.pack_start(self.imgIcon,False,False,1)
		self.imgIcon.show()
		
		#self.lblHead=gtk.Label()
		#self.lblHead.set_markup("<b>lime-ocr</b>")
		#self.headHBox.pack_start(self.lblHead,False,False,1)
		#self.lblHead.show()

		#--- File Selector
		self.dlgFiles = gtk.FileChooserDialog(self.LCselimg, None,\
					        gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,\
					        gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		self.dlgFiles.set_select_multiple(True)
		self.dlgFiles.set_current_folder(os.getenv('USERPROFILE'))
		#self.filterFiles = gtk.FileFilter()
		#self.filterFiles.add_pattern("*")
		#self.filterFiles.set_name("Images Only")
		#self.filterFiles.add_pattern("*.jpg")
		#self.filterFiles.add_pattern("*.jpg")
		#self.filterFiles.add_pattern("*.jpg")
		#self.filterFiles.add_pattern("*.jpg")
		#self.filterFiles.add_mime_type("image/png")
		#self.filterFiles.add_mime_type("image/tiff")
		#self.filterFiles.add_mime_type("image/jpeg")
		#self.filterFiles.add_mime_type("image/bmp")
		#self.dlgFiles.add_filter(self.filterFiles)
		self.dlgFiles.connect("response", self.f_load_files)

		self.lblSelectfile = gtk.Label()
		self.lblSelectfile.set_markup("<small><b>"+self.LCselimg+"</b></small>")
		self.vboxLeft.pack_start(self.lblSelectfile, False, False, 1)
		self.lblSelectfile.show()

		self.btnFiles = gtk.FileChooserButton(self.dlgFiles)
		self.btnFiles.set_current_folder(os.getenv('USERPROFILE'))
		#self.btnFiles.set_title("home")
		self.btnFiles.set_width_chars(18)
		self.vboxLeft.pack_start(self.btnFiles, False, False, 1)
		self.btnFiles.set_filename(self.LCopen)
		self.btnFiles.show()

		self.lblDirectory = gtk.Label()
		self.lblDirectory.set_markup("<small><b>"+self.LCoutfolder+"</b></small>")
		self.vboxLeft.pack_start(self.lblDirectory, False, False, 1)
		self.lblDirectory.show()

		self.dlgDestFolder=gtk.FileChooserDialog(self.LCoutfoldertext\
								, None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER \
								, (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL\
								, gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		self.btnDirectory = gtk.FileChooserButton(self.dlgDestFolder)
		self.btnDirectory.set_current_folder(os.getenv('USERPROFILE'))
		self.btnDirectory.connect("current_folder_changed"\
							, self.f_output_filename,None)

		self.btnDirectory.set_width_chars(10)
		self.vboxLeft.pack_start(self.btnDirectory, False, False, 1)
		self.btnDirectory.show()

		#---Images List
		self.imgList = gtk.ListStore(str)

		self.treeView = gtk.TreeView(self.imgList)
		self.treeView.connect("row-activated", self.f_show_img,None,False)
		self.tvSeleccion = self.treeView.get_selection()
		self.tvSeleccion.connect("changed", self.f_show_img,None,None,None,True)
		self.cell = gtk.CellRendererText()
		self.tvColumn = gtk.TreeViewColumn("", self.cell, text=0)
		self.treeView.append_column(self.tvColumn)
		self.treeView.show()

		self.scrollFiles = gtk.ScrolledWindow()
		self.vboxLeft.pack_start(self.scrollFiles, True, True, 1)
		self.scrollFiles.set_size_request(300,100)
		self.scrollFiles.show()
		self.scrollFiles.add(self.treeView)




#-- OCR -----------------
# Pack-ends
		#--Concatenate--

		self.dlgConcat = gtk.FileChooserDialog(self.LCseltxt, None,\
					        gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,\
					        gtk.RESPONSE_CANCEL,self.LCconcat,gtk.RESPONSE_OK))
		self.dlgConcat.set_select_multiple(True)
		#self.filterText = gtk.FileFilter()
		#self.filterText.add_mime_type("text/plain")
		#self.dlgConcat.add_filter(self.filterText)
		self.dlgConcat.connect("response", self.f_concat_files)

		self.btnConcat = gtk.FileChooserButton(self.dlgConcat)
		self.btnConcat.set_current_folder(os.getenv('USERPROFILE'))
		self.btnConcat.set_width_chars(18)
		self.vboxLeft.pack_end(self.btnConcat, False, False, 3)
		self.btnConcat.show()

		self.hboxConcat1 = gtk.HBox(False, 3)
		self.vboxLeft.pack_end(self.hboxConcat1, False, False, 1)
		self.hboxConcat1.show()

		self.lblConcatnom = gtk.Label()
		self.lblConcatnom.set_markup(" "+self.LCconcatnom)
		self.hboxConcat1.pack_start(self.lblConcatnom, False, False, 1)
		self.lblConcatnom.show()

		self.edtConcat =  gtk.Entry(20)
		self.edtConcat.set_width_chars(9)
		self.edtConcat.set_text("final_text")
		self.edtConcat.set_width_chars(15)
		self.hboxConcat1.pack_start(self.edtConcat, False, False, 1)
		#self.edtConcat.connect("changed", self.f_output_filename, None)
		self.edtConcat.show()

		self.lblConcatext = gtk.Label()
		self.lblConcatext.set_markup(" .txt")
		self.hboxConcat1.pack_start(self.lblConcatext, False, False, 1)
		self.lblConcatext.show()

		self.hboxConcat = gtk.HBox(False, 3)
		self.vboxLeft.pack_end(self.hboxConcat, False, False, 1)
		self.hboxConcat.show()

		self.lblConcattit = gtk.Label()
		self.lblConcattit.set_markup(" <b>"+self.LCconcat+"</b>")
		self.hboxConcat.pack_start(self.lblConcattit, False, False, 1)
		self.lblConcattit.show()

		self.lblConcat = gtk.Label()
		self.lblConcat.set_markup(" <small>"+self.LCconcattext+"</small>")
		self.hboxConcat.pack_start(self.lblConcat, False, False, 1)
		self.lblConcat.show()





		#--OCR--
		self.frameOcr = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameOcr, False, False, 1)
		self.frameOcr.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameOcr.show()

		self.vboxOcr = gtk.VBox(False,5)
		self.frameOcr.add(self.vboxOcr)
		self.vboxOcr.show()

		#--Page--

		self.hboxProcess = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxProcess)
		self.hboxProcess.show()

		self.btnProcess = gtk.Button(self.LCrun,gtk.STOCK_EXECUTE,False)
		self.btnProcess.set_use_stock(True)
		self.btnProcess.connect("clicked", self.f_process_img)
		self.hboxProcess.pack_start(self.btnProcess, True, True, 3)

		self.btnProcess.show()

		self.vboxProcess = gtk.VBox(False,1)
		self.hboxProcess.pack_end(self.vboxProcess,False, False,1)
		self.vboxProcess.show()

		self.rdAllimages = gtk.RadioButton(None,self.LCall,False)
		self.vboxProcess.pack_start(self.rdAllimages, True, False, 1)
		self.rdAllimages.show()

		self.rdSelectedimages = gtk.RadioButton(self.rdAllimages\
								,self.LCselected,False)
		self.vboxProcess.pack_start(self.rdSelectedimages, True, False, 1)
		self.rdSelectedimages.show()

		self.hboxPager = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxPager, False, False,1)
		self.hboxPager.hide()

		self.vboxPagePrefix = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagePrefix, False, False, 1)
		self.vboxPagePrefix.show()


		self.vboxPagStart = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagStart, False, False, 1)
		self.vboxPagStart.show()

		self.vboxPagStep = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxPagStep, False, False, 1)
		self.vboxPagStep.show()

		self.edtPagePrefix =  gtk.Entry(20)
		self.edtPagePrefix.set_width_chars(12)
		self.edtPagePrefix.set_text("page_")
		self.vboxPagePrefix.pack_end(self.edtPagePrefix, False, False, 1)
		self.edtPagePrefix.connect("changed", self.f_output_filename, None)
		self.edtPagePrefix.show()


		self.lblInit = gtk.Label()
		self.lblInit.set_markup(self.LCstart)
		self.vboxPagStart.pack_start(self.lblInit, False, False, 1)
		self.lblInit.show()

		self.edtInitPage =  gtk.SpinButton()
		self.vboxPagStart.pack_start(self.edtInitPage, False, False, 1)
		self.edtInitPage.set_adjustment(gtk.Adjustment(0, 1, 9999, 1, 1))
		self.edtInitPage.set_value(1)
		self.edtInitPage.set_width_chars(4)
		self.edtInitPage.connect("changed", self.f_output_filename, None)
		self.edtInitPage.show()


		self.lblStep = gtk.Label()
		self.lblStep.set_markup(self.LCstep)
		self.vboxPagStep.pack_start(self.lblStep, False, False, 1)
		self.lblStep.show()

		self.edtPageStep =  gtk.SpinButton()
		self.vboxPagStep.pack_start(self.edtPageStep, False, False, 1)
		self.edtPageStep.set_adjustment(gtk.Adjustment(0, 1, 4, 1, 1))
		self.edtPageStep.set_value(1)
		self.edtPageStep.set_width_chars(1)
		self.edtPageStep.connect("changed", self.f_output_filename, None)
		self.edtPageStep.show()


		self.vboxColumn = gtk.VBox(False,1)
		self.hboxPager.pack_start(self.vboxColumn, False, False, 1)
		self.vboxColumn.show()

		self.lblCol = gtk.Label()
		self.lblCol.set_markup(self.LCcolumn)
		self.vboxColumn.pack_start(self.lblCol, False, False, 1)
		self.lblCol.show()

		self.edtCol =  gtk.SpinButton()
		self.vboxColumn.pack_start(self.edtCol, False, False, 1)
		self.edtCol.set_adjustment(gtk.Adjustment(0, 0, 6, 1, 1))
		self.edtCol.set_value(0)
		self.edtCol.set_width_chars(1)
		self.edtCol.connect("changed", self.f_output_filename, None)
		self.edtCol.show()


		self.chkPageNumbering = gtk.CheckButton(self.LCindextext,True)
		self.vboxOcr.pack_end(self.chkPageNumbering, False, False, 1)
		self.chkPageNumbering.connect("clicked", self.f_output_filename,None)
		self.chkPageNumbering.show()

		#--Language--
		self.hboxLanguage = gtk.HBox(False, 3)
		self.vboxOcr.pack_end(self.hboxLanguage)
		self.hboxLanguage.show()

		self.cmbLang = gtk.combo_box_new_text()
		self.hboxLanguage.pack_end(self.cmbLang, False, False, 1)
		self.cmbLang.connect("changed" , self.f_lang_choice)
		self.cmbLang.show()

		self.lblLan = gtk.Label()
		self.lblLan.set_markup(self.LClanguage)
		self.hboxLanguage.pack_end(self.lblLan, False, False, 1)
		self.lblLan.show()

		self.lblOcr = gtk.Label()
		self.lblOcr.set_markup(" <b>"+self.LCocr+"</b>")
		self.hboxLanguage.pack_start(self.lblOcr, False, False, 1)
		self.lblOcr.show()



		# Rotate
		self.frameRotate = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameRotate, False, False, 1)
		self.frameRotate.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameRotate.show()

		self.vboxRotate = gtk.VBox(False,5)
		self.frameRotate.add(self.vboxRotate)
		self.vboxRotate.show()

		self.hboxRotButlbl = gtk.HBox(False, 3)
		self.vboxRotate.pack_start(self.hboxRotButlbl, False, False,1)
		self.hboxRotButlbl.show()

		self.lblRotate = gtk.Label()
		self.lblRotate.set_markup(" <small><b>"+self.LCrotate+"</b></small> ")
		self.hboxRotButlbl.pack_start(self.lblRotate, False, False,1)
		self.lblRotate.show()

		self.hboxRotBut = gtk.HBox(False, 3)
		self.vboxRotate.pack_start(self.hboxRotBut, False, False,1)
		self.hboxRotBut.show()


		self.edtRotAngle =  gtk.SpinButton()
		self.hboxRotBut.pack_start(self.edtRotAngle, False, False, 1)
		self.edtRotAngle.set_width_chars(4)
		self.edtRotAngle.set_adjustment(gtk.Adjustment(0, -180, 180, 1, 1))
		self.edtRotAngle.set_text("0")
		self.edtRotAngle.connect("button-press-event",self.f_angle_press)
		self.edtRotAngle.connect("focus-in-event",self.f_angle_press)
		self.edtRotAngle.connect("button-release-event",self.f_angle_value)
		self.edtRotAngle.connect("focus-out-event",self.f_angle_value)
		self.edtRotAngle.connect("activate",self.f_angle_value)
		self.edtRotAngle.show()



		self.btnResRot = gtk.Button(self.LCreset)
		self.btnResRot.connect("clicked", self.f_angle_change,None, True)
		self.hboxRotBut.pack_start(self.btnResRot, False, False, 1)
		self.btnResRot.show()

		#self.lblRotate = gtk.Label()
		#self.lblRotate.set_markup(" Degrees")
		#self.hboxRotBut.pack_start(self.lblRotate, False, False, 1)
		#self.lblRotate.show()

		self.btnResRot = gtk.Button(self.LCgeneralize)
		self.btnResRot.connect("clicked", self.f_generallize,5)
		self.hboxRotBut.pack_end(self.btnResRot, False, False, 1)
		self.btnResRot.show()

		self.rotateDegrees = gtk.HScrollbar()
		self.vboxRotate.pack_start(self.rotateDegrees, True, True, 1)
		self.rotateDegrees.show()
		self.rotateDegrees.set_adjustment(gtk.Adjustment\
						(0 , (-180) , (180)+1 , 1 ,1 , 1))

		self.rotateDegrees.set_value(0)
		self.rotateDegrees.connect("value-changed",self.f_angle_change2)
		self.rotateDegrees.connect("button-release-event" \
						, self.f_angle_change, False)



		# Crop
		self.frameCrop = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameCrop, False, False, 1)
		self.frameCrop.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameCrop.show()



		self.vboxCrop = gtk.VBox(False,5)
		self.frameCrop.add(self.vboxCrop)
		self.vboxCrop.show()

		self.hboxCroplb = gtk.HBox(False,5)
		self.vboxCrop.pack_start(self.hboxCroplb,False,False,1)
		self.hboxCroplb.show()

		self.lblCrop = gtk.Label()
		self.lblCrop.set_markup(" <small><b>"+self.LCcrop+"</b>\n "+self.LCcroptext+"</small>")
		self.hboxCroplb.pack_start(self.lblCrop,False,False,1)
		self.lblCrop.show()

		self.hboxCrop = gtk.HBox(False,5)
		self.vboxCrop.pack_start(self.hboxCrop,False,False,1)
		self.hboxCrop.show()

		self.vboxCropL = gtk.VBox(False,5)
		self.hboxCrop.pack_start(self.vboxCropL,False,False,1)
		self.vboxCropL.show()

		self.hboxCropL = gtk.HBox(False,5)
		self.vboxCropL.pack_start(self.hboxCropL,False,False,1)
		self.hboxCropL.show()

		self.lblCropL = gtk.Label()
		self.lblCropL.set_markup(" <small>"+self.LCleft+":</small> ")
		self.hboxCropL.pack_start(self.lblCropL, False, False, 1)
		self.lblCropL.show()

		self.hboxCropT = gtk.HBox(False,5)
		self.vboxCropL.pack_start(self.hboxCropT,False,False,1)
		self.hboxCropT.show()

		self.lblCropT = gtk.Label()
		self.lblCropT.set_markup(" <small>"+self.LCtop+":</small> ")
		self.hboxCropT.pack_start(self.lblCropT, False, False, 1)
		self.lblCropT.show()

		self.vboxCropC = gtk.VBox(False,5)
		self.hboxCrop.pack_start(self.vboxCropC,True,True,1)
		self.vboxCropC.show()

		self.hboxCropR = gtk.HBox(False,5)
		self.vboxCropC.pack_start(self.hboxCropR,False,False,1)
		self.hboxCropR.show()

		self.lblCropR = gtk.Label()
		self.lblCropR.set_markup(" <small>"+self.LCright+":</small> ")
		self.hboxCropR.pack_start(self.lblCropR, False, False, 1)
		self.lblCropR.show()

		self.hboxCropB = gtk.HBox(False,5)
		self.vboxCropC.pack_start(self.hboxCropB,False,False,1)
		self.hboxCropB.show()

		self.lblCropB = gtk.Label()
		self.lblCropB.set_markup(" <small>"+self.LCbottom+":</small> ")
		self.hboxCropB.pack_start(self.lblCropB, False, False, 1)
		self.lblCropB.show()

		self.vboxCropR = gtk.VBox(False,5)
		self.hboxCrop.pack_end(self.vboxCropR,False,True,1)
		self.vboxCropR.show()

		self.btnCrop = gtk.Button(self.LCgeneralize)
		self.btnCrop.connect("clicked", self.f_generallize,6)
		self.vboxCropR.pack_end(self.btnCrop, False, False, 1)
		self.btnCrop.show()


		# Normalize
		self.frameProc = gtk.Frame(None)
		self.vboxLeft.pack_end(self.frameProc, False, False, 1)
		self.frameProc.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameProc.show()

		self.vboxProc = gtk.VBox(False,5)
		self.frameProc.add(self.vboxProc)
		self.vboxProc.show()

		self.hboxNorm = gtk.HBox(False,5)
		self.vboxProc.pack_start(self.hboxNorm,False,False,1)
		self.hboxNorm.show()

		self.lblNormalize = gtk.Label()
		self.lblNormalize.set_markup(" <small><b>"+self.LCnormalize+"</b></small> ")
		self.hboxNorm.pack_start(self.lblNormalize, False, False, 1)
		self.lblNormalize.show()

		self.chkNormalize = gtk.CheckButton("", True)
		self.chkNormalize.set_active(False)
		self.hboxNorm.pack_start(self.chkNormalize, False, False, 1)
		self.chkNormalize.connect("clicked", self.f_normalize_change)
		self.chkNormalize.show()

		self.btnNormalize = gtk.Button(self.LCgeneralize)
		self.btnNormalize.connect("clicked", self.f_generallize,4)
		self.hboxNorm.pack_end(self.btnNormalize, False, False, 1)
		self.btnNormalize.show()


		# Right of Window ---------------------------------
		self.vboxRight = gtk.VBox(False, 1)
		self.hboxWindow.pack_start(self.vboxRight, True, True, 2)
		self.vboxRight.show()


		# Preview Buttons
		self.framePrevOp = gtk.Frame(None)
		self.vboxRight.pack_start(self.framePrevOp, False, False, 1)
		self.framePrevOp.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.framePrevOp.show()
		
		self.hboxPrevOp = gtk.HBox(False,1)
		self.framePrevOp.add(self.hboxPrevOp)
		self.hboxPrevOp.show()

		self.btnAutoPrev = gtk.ToggleButton("Auto Resize", False)
		self.hboxPrevOp.pack_start(self.btnAutoPrev, False, False, 1)
		self.btnAutoPrev.connect("clicked", self.f_show_buttons)
		self.btnAutoPrev.set_mode(True)
		self.btnAutoPrev.show()

		self.btnPrevMax = gtk.Button("",gtk.STOCK_ZOOM_FIT,False)
		self.btnPrevMax.connect("clicked", self.f_show_img,None,None,None,False)
		self.hboxPrevOp.pack_start(self.btnPrevMax, False, False, 1)
		self.btnPrevMax.show()

		self.btnPrevPlus = gtk.Button("",gtk.STOCK_ZOOM_IN,False)
		self.btnPrevPlus.connect("clicked", self.f_show_img,None,None,1.1,False)
		self.hboxPrevOp.pack_start(self.btnPrevPlus, False, False, 1)
		self.btnPrevPlus.show()

		self.btnPrevMinus = gtk.Button("",gtk.STOCK_ZOOM_OUT,False)
		self.btnPrevMinus.connect("clicked", self.f_show_img,None,None,0.9,False)
		self.hboxPrevOp.pack_start(self.btnPrevMinus, False, False, 1)
		self.btnPrevMinus.show()


		#---Show Window
		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
		self.vboxRight.pack_start(self.scrolledwindow, True, True, 2)
		self.scrolledwindow.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
		#self.scrolledwindow.connect("button-press-event", self.f_coord)
		#self.scrolledwindow.set_size_request(400,100)
		self.scrolledwindow.show()

		self.drawingArea = gtk.DrawingArea()
		self.drawingArea.set_size_request(0,0)
		self.drawingArea.set_events(gtk.gdk.EXPOSURE_MASK \
			| gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.BUTTON_PRESS_MASK \
			| gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK \
			| gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_RELEASE \
			| gtk.gdk.MOTION_NOTIFY )
		                        
		self.drawingArea.connect("expose-event",self.f_redraw_area)
		self.drawingArea.connect("button_press_event",self.f_init_rect,1)
		self.drawingArea.connect("button_release_event",self.f_init_rect,0)
		self.drawingArea.connect("motion_notify_event",self.f_draw_rect,1)
		self.scrolledwindow.add_with_viewport(self.drawingArea)
		self.drawingArea.show()

		# Frame Info
		self.frameInfo = gtk.Frame(None)
		self.vboxRight.pack_start(self.frameInfo, False, False, 1)
		self.frameInfo.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.frameInfo.show()

		self.vboxInfo = gtk.VBox(False, 1)
		self.frameInfo.add(self.vboxInfo)
		self.vboxInfo.show()

		self.hboxInfoIn = gtk.HBox(False, 1)
		self.vboxInfo.add(self.hboxInfoIn)
		self.hboxInfoIn.show()

		self.lblInfoIn = gtk.Label()
		self.lblInfoIn.set_markup("<small><b> "+self.LCimage+": </b></small>(none)")
		self.hboxInfoIn.pack_start(self.lblInfoIn, False, False, 1)
		self.lblInfoIn.show()

		self.hboxInfoOut = gtk.HBox(False, 1)
		self.vboxInfo.add(self.hboxInfoOut)
		self.hboxInfoOut.show()

		self.lblInfoOut = gtk.Label()
		self.lblInfoOut.set_markup("<small><b> "+self.LCtextfile+": </b></small>(none)")
		self.hboxInfoOut.pack_start(self.lblInfoOut, False, False, 1)
		self.lblInfoOut.show()

		# Show the window-------------------------------------------------------
		self.mainwindow.show()
		self.f_init_variables()
		self.f_create_lang()
	# __init__ END

################################################################################
### Functions-------------------------------------------------------------------
	### Importatnt Functions ---------------------------------------------------

	def f_init_variables(self):
		print "reseting variables..."
		self.Scale=None
		self.Images=[]
		self.ImageWidth=None
		self.ImageHeight=None
		self.Selected=None
		self.pixBuf=None
		self.pixBufPrev=None
		self.Pressed=None
		self.rectangle=None
		self.Home = os.environ['USERPROFILE'] + "\\"
		self.ConfFile = ".lime-ocrrc"
		self.f_read_conf()
		self.DibujaArea=0
		self.Pressed=0
		self.ProcessedFiles=[]
		self.btnFiles.set_current_folder(self.Home)
		self.PgStt=1
		self.PgStp=1
		self.PgClm=0



	#}} f_init_variables END

	def f_load_files(self, widget, Data):
		if Data == -5 :
			self.f_init_variables()
			self.imgList.clear() 
			self.DirectoryIn = self.dlgFiles.get_current_folder() + "\\"
			self.FolderOut= self.DirectoryIn
			self.btnConcat.set_current_folder(self.FolderOut)
			self.btnDirectory.set_current_folder(self.FolderOut) # Output Folder
			self.tvColumn.set_title(self.DirectoryIn) # Column Title
			self.Files=self.dlgFiles.get_filenames()
			if self.Files :
				print "\nLoading images from: " + self.DirectoryIn
				nnfin = len(self.Files)
				for nn in range(0,nnfin) :
					File = self.Files[nn]
					(Path,Image) = File.rsplit("\\",1)
					(Name,Ext) = Image.rsplit(".",1)
					Ext = "." + Ext
					self.imgList.append([Image])
					#### ---- Images is a list:
			    		# ------- 0=Index
					# ------- 1=Image
					# ------- 2=Name
					# ------- 3=Extension
					# ------- 4=Normalize
					# ------- 5=Rotate
					# ------- (6=Rectangles)[n]
					if self.chkNormalize.get_active() == True : Norm = True
					else : Norm = False
					rect=None 
					self.Images.append([nn,Image,Name,Ext,Norm,0,[rect]])
					print " " + Image

		self.btnFiles.set_current_folder(self.btnFiles.get_current_folder())
	#}} f_load_files END

	def f_show_img(self,widget,Data,Data2,Zoom,WritePrev):
		#----- Image = (self.Images[self.Selected])[1]
		#----- Name = (self.Images[self.Selected])[2]
		#----- Ext = (self.Images[self.Selected])[3]
		#----- Norm = (self.Images[self.Selected])[4]
		#----- Rotate = (self.Images[self.Selected])[5]
		#----- Rect = (self.Images[self.Selected])[6]
		                                            
		self.f_select_img()

		ScrolledWidth = self.scrolledwindow.allocation.width - 30

		if self.Selected != None:
			self.f_output_filename(None,self.Selected)
			Index = (self.Images[self.Selected])[0]
			Image = (self.Images[self.Selected])[1]
			Name = (self.Images[self.Selected])[2]
			Ext = (self.Images[self.Selected])[3]
			Norm = (self.Images[self.Selected])[4]
			Rotate = (self.Images[self.Selected])[5]
			Rect = (self.Images[self.Selected])[6]

			self.chkNormalize.set_active(Norm)
			self.rotateDegrees.set_value(int(float(Rotate)))
			self.rectangle = Rect[0]

			if WritePrev == True:
				rotate_option = self.f_opRotate(Index)
				normalize_option = self.f_opNormalize(Index)
				options= normalize_option + " " + rotate_option 
				runBash("convert -quality 80 " + options + " \"" \
								+ self.DirectoryIn + Image \
								+ "[0]\" \"tmp\\tesseract_preview.jpg\"")

				self.pixBuf=gtk.gdk.pixbuf_new_from_file\
								("tmp\\tesseract_preview.jpg")

				self.ImageW = self.pixBuf.get_width()
				self.ImageH = self.pixBuf.get_height()

			if Zoom and self.Scale:
				self.Scale = self.Scale * Zoom
			else:
				self.Scale = (float(ScrolledWidth) / float(self.ImageW))

			self.Interp = gtk.gdk.INTERP_NEAREST

			self.drawingArea.set_size_request(int(self.ImageW * self.Scale)\
							,int(self.ImageH * self.Scale))

			self.pixBufPrev = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8\
							,int(self.ImageW*self.Scale)\
							,int(self.ImageH*self.Scale))

			self.pixBuf.scale(self.pixBufPrev,0,0,int(self.ImageW * self.Scale)\
							,int(self.ImageH * self.Scale),0,0\
							,self.Scale,self.Scale,self.Interp)

			self.f_redraw_area(self,None)
	#}} f_show_img END

	def f_redraw_area(self, widget, event):
		gc = self.drawingArea.get_style().fg_gc[gtk.STATE_NORMAL]
		colormap= self.drawingArea.get_colormap()
		color = colormap.alloc_color(40000,0,0,False,False)
		gcArea = self.drawingArea.window.new_gc()
		gcArea.set_foreground(color)
		gcArea.set_dashes(15, (6,6))
		gcArea.line_width = 2
		gcArea.line_style = gtk.gdk.LINE_ON_OFF_DASH
		gcHand = self.drawingArea.window.new_gc()
		gcHand.set_foreground(color)
		gcHand.line_width = 3
		gcHand.line_style = gtk.gdk.SOLID
		gcHand.fill = gtk.gdk.SOLID
		ScrolledWidth =  self.scrolledwindow.allocation.width - 30
		Scale = self.Scale
		if self.pixBufPrev:

			if self.btnAutoPrev.get_active() == True:
				Scale = (float(ScrolledWidth) / float(self.ImageW))
				self.pixBufPrev = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8\
								,int(self.ImageW*Scale),int(self.ImageH*Scale))

				self.pixBuf.scale(self.pixBufPrev,0,0,int(self.ImageW*Scale)\
							,int(self.ImageH*Scale),0,0,Scale,Scale,self.Interp)

				self.drawingArea.set_size_request(int(self.ImageW * Scale)\
							,int(self.ImageH * Scale))

			self.drawingArea.window.draw_pixbuf(gc, self.pixBufPrev, 0, 0, 0, 0)

			if self.rectangle :
				x = self.rectangle.x
				y = self.rectangle.y
				xx = (self.rectangle.x + self.rectangle.width)
				yy = (self.rectangle.y + self.rectangle.height)
				w = self.rectangle.width
				h = self.rectangle.height
				rectx = int(x * Scale)
				recty = int(y * Scale)
				rectxx = int((x + w) * Scale)
				rectyy = int((y + h) * Scale)
				rectw = int(w * Scale)
				recth = int(h * Scale)

				self.drawingArea.window.draw_rectangle( gcArea , False \
								, rectx , recty , rectw , recth)

				self.drawingArea.window.draw_rectangle( gcHand , False \
								, (rectx + 5) , (recty + 5 ) , 10 ,10)

				self.drawingArea.window.draw_rectangle( gcHand , False \
								, (rectxx-7) , ( rectyy-7) , 5 , 5 )

			else:
				x = ""
				y = ""
				xx = ""
				yy = ""
			self.lblCropL.set_markup(" <small>"+self.LCleft+":</small> " + str(x))
			self.lblCropR.set_markup(" <small>"+self.LCright+":</small> " + str(xx))
			self.lblCropT.set_markup(" <small>"+self.LCtop+":</small> " + str(y))
			self.lblCropB.set_markup(" <small>"+self.LCbottom+":</small> " + str(yy))
			self.Scale = Scale
	#}} f_redraw_area END

	def f_process_img(self,widget):
		self.dialogInfo = self.Dialogo()
		self.dialogInfo.create("info",self.LCprocess,"hide")

		ImagesToProcess=[]
		if self.rdAllimages.get_active() :
			if len(self.Images) > 0: ImagesToProcess = self.Images
		elif self.rdSelectedimages.get_active() :
			if self.Selected != None : ImagesToProcess.append(\
							self.Images[self.Selected])
		else:
			ImagesToProcess=[]

		if len(ImagesToProcess) > 0 and self.dialogInfo:
			nnfin = len(ImagesToProcess)
			for nn in range(0,nnfin):
				self.ProcessOrder="yes"
				Index = (ImagesToProcess[nn])[0]
				Image = (ImagesToProcess[nn])[1]
				Name = (ImagesToProcess[nn])[2]
				Ext = (ImagesToProcess[nn])[3]
				Norm = (ImagesToProcess[nn])[4]
				Rotate = (ImagesToProcess[nn])[5]
				Rect = (ImagesToProcess[nn])[6]
				normalize_option = self.f_opNormalize(Index)
				rotate_option = self.f_opRotate(Index)
				crop_option = self.f_opCrop(Index)
				options= rotate_option +" "+crop_option + " " + normalize_option
				NameOut = self.f_output_filename(None,Index)
				FileIn = self.DirectoryIn + Image

				self.dialogInfo.change("info",self.LCprocess + "\n" + NameOut,"hide")
				

				Comprueba = runBash("ls \"" + self.FolderOut \
						+ NameOut + ".txt\"")
				if Comprueba :
					self.dialogInfo.change("error",self.LCabort1+"<b>"\
						+ self.FolderOut + NameOut+".txt</b>","show")
					self.ProcessOrder="no"
					
					#self.dialogInfo.destroy(None,"cancel")

				if self.ProcessOrder == "yes":
					self.ProcessedFiles.append(NameOut)
					

					Processtif = "tmp\\tesseract_process"+str(nn)+".tif"
					Processjpg = "tmp\\tesseract_process"+str(nn)+".jpg"

					runBash("convert -compress None \"" + FileIn + "[0]\" " \
									+ Processjpg + "" )

					runBash("convert -compress None \"" + Processjpg + "\" " \
									+ rotate_option + " \"" + Processtif + "\"" )
					runBash("rm " + Processjpg  + "")

					if normalize_option :
						runBash("mogrify " + normalize_option + " " \
									+ Processtif + "")
					if crop_option :
						runBash("mogrify " + crop_option + " "  \
									+ Processtif + "" )

					runBash("mogrify -antialias " + Processtif  + "")
					runBash("mogrify -monochrome " + Processtif  + "")

						                                      
					runBash("tesseract \"" + Processtif + "\" \"" + self.FolderOut  \
									+ NameOut + "\" -l " + lang  + "")

					print "Recognition: "+self.FolderOut+NameOut+"\" Language: "+lang
					runBash("rm " + Processtif  + "")

					print self.LCprocessend
					self.ProcessedFiles.sort()
					print self.ProcessedFiles
					self.dialogInfo.change("info",self.LCprocessend,"show")
	# f_process_img END



	### Secondary Functions-----------------------------------------------------

	def f_select_img(self):
		if self.tvSeleccion.get_selected_rows()[1] != []:
			Sel = self.tvSeleccion.get_selected_rows()[1]
			Selected = ((self.tvSeleccion.get_selected_rows()[1])[0])[0]
			self.Selected = Selected
			return Selected
	#}} f_select_img END


	def f_output_filename(self,widget,Index):
		self.f_destination_folder(self,None)
		NameOut = self.LCnameoffile

		if self.Images:
			
			if Index == None : 
				Index = self.Selected
			if self.chkPageNumbering.get_active() == True:
				self.hboxPager.show()
				if Index != None and self.edtInitPage.get_text() != '': 

					if int(self.edtCol.get_text()) == 0:
						Column = ""
					elif int(self.edtCol.get_text()) != 0 or self.edtCol.get_text() != None:
						Column = "-col_" + self.edtCol.get_text()

					Page = (int(self.edtInitPage.get_text()) \
								+ (int(self.edtPageStep.get_text() )*Index ))

					NameOut = (self.edtPagePrefix.get_text() + str( Page ) + str(Column)) 
				else:
					NameOut = self.edtPagePrefix.get_text() + "(index)"
			else:
				self.hboxPager.hide()
				if Index != None :
					NameOut = (self.Images[Index])[2]
					self.lblInfoIn.set_markup("<small><b> "+self.LCimage+":</b></small> "\
									+ self.DirectoryIn + (self.Images[Index])[1])
				else:
					self.lblInfoIn.set_markup("<small><b> "+self.LCimage+":</b></small> "\
									+ self.DirectoryIn + NameOut)


			self.lblInfoOut.set_markup("<small><b> "+self.LCtextfile+":</b></small> " \
									+ self.FolderOut  + NameOut + ".txt")			
			return NameOut
		else:
			self.chkPageNumbering.set_active(False)

	#}} f_output_filename END

	def f_destination_folder(self,widget,Data):
		self.FolderOut = self.btnDirectory.get_current_folder() + "\\"
		self.btnConcat.set_current_folder(self.FolderOut)
		return self.FolderOut		
	#}} f_destination_folder END

	def f_show_buttons(self,widget):
		if self.btnAutoPrev.get_active() == True:
			self.btnPrevMinus.hide()
			self.btnPrevMax.hide()
			self.btnPrevPlus.hide()
			self.f_show_img(None,None,None,None,False)
		if self.btnAutoPrev.get_active() == False:
			self.btnPrevMinus.show()
			self.btnPrevMax.show()
			self.btnPrevPlus.show()
			self.f_show_img(None,None,None,None,False)
	#}} f_show_buttons END

	def f_angle_change(self , widget,Dato, Reset):
		if Reset: self.rotateDegrees.set_value(0)
		angle = (int (self.rotateDegrees.get_value()) )
		angulo = str(angle)
		self.f_angle_change2(None)
		if self.Selected != None:
			(self.Images[self.Selected])[5] = angulo
		self.f_show_img(None,None,None,1,True)
	# f_angle_change END

	def f_angle_change2(self,widget):
		self.edtRotAngle.set_text(str(int(self.rotateDegrees.get_value())))

	# f_angle_change2 END

	def f_angle_press(self,widget,Data):
		self.AnglePress=self.edtRotAngle.get_text()
	# f_angle_press END	

	def f_angle_value(self,widget,Data=None):
		#self.edtRotAngle.set_value(self.rotateDegrees.get_value()) ####################
		if self.AnglePress != self.edtRotAngle.get_text():
			self.rotateDegrees.set_value(int(self.edtRotAngle.get_text()))
			self.f_angle_change(None,None,False)
	# f_angle_change2 END

	def f_normalize_change(self,widget):
		if self.Selected != None:
			(self.Images[self.Selected])[4] = self.chkNormalize.get_active()
		self.f_show_img(None,None,None,1,True)
	# f_normalize_change END

	def f_init_rect(self,widget,dato, Evento):
		self.x=None
		self.y=None

		Pressx , Pressy , Nada= self.drawingArea.window.get_pointer()

		self.AreaAction="resize"
		self.Pressed = Evento

		if self.Selected != None:
			if Pressx < (self.ImageW * self.Scale)  and Pressy < (self.ImageH * self.Scale) :
				self.DibujaArea=1
			else:
				self.DibujaArea=0

			if self.Pressed == 1 and self.DibujaArea == 1:

				self.Pressx = Pressx
				self.Pressy = Pressy

				self.rectangle = ((self.Images[self.Selected])[6])[0]
				if self.rectangle :
					self.Pressx=None
					self.Pressy=None
					self.x = int((self.rectangle.x) * self.Scale)
					self.y = int((self.rectangle.y)* self.Scale)
					self.xx = int((self.rectangle.x + self.rectangle.width) \
										* self.Scale)

					self.yy = int((self.rectangle.y + self.rectangle.height) \
										* self.Scale)

					if Pressx < (self.xx) and Pressy < (self.yy) and Pressx > \
									(self.x) and Pressy > (self.y) :
	
						self.drawingArea.window.set_cursor(\
									gtk.gdk.Cursor(gtk.gdk.FLEUR))

						self.AreaAction = "move"
						self.Pressx = Pressx
						self.Pressy = Pressy
					if Pressx > (self.x + 6) and Pressy > (self.y + 6)  and \
							Pressx < (self.x  + 16) and Pressy < (self.y + 16) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
											(gtk.gdk.X_CURSOR))

						self.AreaAction="clear"
						self.Pressx=None
						self.Pressy=None
						self.rectangle=None
						((self.Images[self.Selected])[6])[0] = None
						self.f_redraw_area(self,None)
					if Pressx < (self.xx) and Pressy < (self.yy) and \
							Pressx > (self.xx - 7) and Pressy > (self.yy - 7) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.BOTTOM_RIGHT_CORNER))

						self.AreaAction = "resize"
						self.Rectx = self.x
						self.Recty = self.y
		if self.Pressed == 0:
			self.drawingArea.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
		self.f_show_img(None,None,None,1,False)
	# f_init_rect END

	def f_draw_rect(self,widget,dato, evento):

		if self.Selected != None:
			Movex , Movey , Nada= self.drawingArea.window.get_pointer()
			self.rectangle = ((self.Images[self.Selected])[6])[0]
			if self.Pressed == 0 :
				if self.rectangle:
					x = int((self.rectangle.x) * self.Scale)
					y = int((self.rectangle.y)* self.Scale)
					xx = int((self.rectangle.x + self.rectangle.width) \
										* self.Scale)

					yy = int((self.rectangle.y + self.rectangle.height) \
										* self.Scale)

					self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.ARROW))
					if Movex < (xx) and Movey < (yy) and Movex > (x) and \
										Movey > (y) :
	
						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.HAND1))

					if Movex > (x + 6) and Movey > (y + 6)  and Movex < \
										(x  + 16) and Movey < (y + 16) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.X_CURSOR))
					if Movex < (xx) and Movey < (yy) and Movex > (xx - 7) and \
										Movey > (yy - 7) :

						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.HAND2))
				else:
					
					if Movex < int(self.ImageW * self.Scale) and Movex > 0 \
								and Movey < int(self.ImageH * self.Scale) and Movey > 0 :
						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.DRAPED_BOX))
					else: 
						self.drawingArea.window.set_cursor(gtk.gdk.Cursor\
										(gtk.gdk.ARROW))

			if self.Pressed == 1 and self.DibujaArea == 1:
				if self.Pressx and self.Pressy :
					if self.x == None : self.x = self.Pressx
					if self.y == None : self.y = self.Pressy
					if self.rectangle:
						x = int((self.rectangle.x) * self.Scale)
						y = int((self.rectangle.y)* self.Scale)
						xx = int((self.rectangle.x + self.rectangle.width) \
											* self.Scale)

						yy = int((self.rectangle.y + self.rectangle.height) \
											* self.Scale)

						if self.AreaAction == "resize":
							self.Rectxx = xx - (xx - Movex) 
							self.Rectyy = yy - (yy - Movey)
							if Movex < self.x :
								self.Rectxx = self.x
								self.Rectx = Movex
							if Movey < self.y :
								self.Rectyy = self.y
								self.Recty =  Movey

						elif self.AreaAction == "move":

							
							if self.x + (Movex - self.Pressx) > 0 :
								#if Movex == None: Movex = 0
								self.Rectx = self.x + (Movex - self.Pressx)
							else:
								self.Rect = 0
							if self.y + (Movey - self.Pressy) > 0  :
								self.Recty = self.y + (Movey - self.Pressy)
							else:
								self.Recty = 0
							if int((self.xx + (Movex - self.Pressx))  \
										/ self.Scale) < self.ImageW:

								self.Rectxx = self.xx + (Movex - self.Pressx)
							else:
								self.Rectxx = int(self.ImageW  * self.Scale)
							if int((self.yy + (Movey - self.Pressy))  \
										/ self.Scale) < self.ImageH:

								self.Rectyy = self.yy + (Movey - self.Pressy)
							else:
								self.Rectyy = int(self.ImageH  * self.Scale)
							if self.Rectx  > int(self.ImageW * self.Scale) - 10:
								self.Rectx = int(self.ImageW * self.Scale) -10
							if self.Recty  > int(self.ImageH * self.Scale) - 10:
								self.Recty = int(self.ImageH * self.Scale) -10


					else:
						self.Rectx = self.Pressx
						self.Recty = self.Pressy
						self.Rectxx = Movex
						self.Rectyy = Movey
						
						
					cropx = int(self.Rectx / self.Scale)
					cropy = int(self.Recty  / self.Scale)
					cropxx = int(self.Rectxx  / self.Scale)
					cropyy = int(self.Rectyy  / self.Scale)
					if cropx < 0 : cropx = 0
					if cropy < 0 : cropy = 0
					if cropxx > self.ImageW : cropxx = self.ImageW
					if cropyy > self.ImageH : cropyy = self.ImageH
					cropw = cropxx - cropx
					croph = cropyy - cropy

					self.rectangle = gtk.gdk.Rectangle(cropx,cropy,cropw,croph)

					((self.Images[self.Selected])[6])[0] = self.rectangle
					
					self.f_redraw_area(self,None)
	# f_draw_rect END

	def f_generallize(self,widget,Nn):
		if self.Selected != None:
			nnfin = len(self.Images)
			for nn in range(0,nnfin):
				if Nn == 6 :
					((self.Images[nn])[Nn])[0]=((self.Images[self.Selected])[Nn])[0]
				else:
					(self.Images[nn])[Nn] = (self.Images[self.Selected])[Nn]
			self.f_show_img(None,None,None,1,False)
	# f_generallize END

	def f_create_lang(self):
		Languages = {}
		try :
			LanguageFile = open("lang-list.txt", "r")
			linelas = LanguageFile.readlines()
			nnfin = len(linelas)
			for nn in range(0,nnfin):
				if linelas[nn] == "\n": linelas[nn] = None
				if linelas[nn] :
					linea = linelas[nn].rstrip("\n")
					(Key,Value) = linea.split("=",1)
					Languages[Key] = Value
				nn = nn+1
			LanguageFile.close() 
			self.ListLanguages={}
			nnfin=len(Languages)
			Nn=0
			for nn in range (0,nnfin):
				self.ListLanguages[Languages.keys()[nn]]=Languages.values()[nn]
				self.cmbLang.append_text(Languages.keys()[nn])
				if self.ConfVars["Language"] == Languages.values()[nn]:
					self.cmbLang.set_active(Nn)
				Nn = Nn + 1
		except IOError:
			nn = 0
			Languages = { 	"Afar":"aar",\
							"Abkhazian":"abk",\
							"Afrikaans":"afr",\
							"Akan":"aka",\
							"Amharic":"amh",\
							"Arabic":"ara",\
							"Aragonese":"arg",\
							"Assamese":"asm",\
							"Avaric":"ava",\
							"Avestan":"ave",\
							"Aymara":"aym",\
							"Azerbaijani":"aze",\
							"Bashkir":"bak",\
							"Bambara":"bam",\
							"Belarusian":"bel",\
							"Bengali":"ben",\
							"Bihari":"bih",\
							"Bislama":"bis",\
							"Tibetan":"bod",\
							"Bosnian":"bos",\
							"Breton":"bre",\
							"Bulgarian":"bul",\
							"Catalan":"cat",\
							"Czech":"ces",\
							"Chamorro":"cha",\
							"Chechen":"che",\
							"Church Slavic":"chu",\
							"Chuvash":"chv",\
							"Cornish":"cor",\
							"Corsican":"cos",\
							"Cree":"cre",\
							"Welsh":"cym",\
							"Danish":"dan",\
							"German":"deu",\
							"Divehi":"div",\
							"Dzongkha":"dzo",\
							"Modern Greek":"ell",\
							"English":"eng",\
							"Esperanto":"epo",\
							"Estonian":"est",\
							"Basque":"eus",\
							"Ewe":"ewe",\
							"Faroese":"fao",\
							"Persian":"fas",\
							"Fijian":"fij",\
							"Finnish":"fin",\
							"French":"fra",\
							"Western Frisian":"fry",\
							"Fulah":"ful",\
							"Gaelic":"gla",\
							"Irish":"gle",\
							"Galician":"glg",\
							"Manx":"glv",\
							"Guaran":"grn",\
							"Gujarati":"guj",\
							"Haitian":"hat",\
							"Hausa":"hau",\
							"Modern Hebrew":"heb",\
							"Herero":"her",\
							"Hindi":"hin",\
							"Hiri Motu":"hmo",\
							"Croatian":"hrv",\
							"Hungarian":"hun",\
							"Armenian":"hye",\
							"Igbo":"ibo",\
							"Ido":"ido",\
							"Sichuan Yi":"iii",\
							"Inuktitut":"iku",\
							"Interlingue":"ile",\
							"Interlingua":"ina",\
							"Indonesian":"ind",\
							"Inupiaq":"ipk",\
							"Icelandic":"isl",\
							"Italian":"ita",\
							"Javanese":"jav",\
							"Japanese":"jpn",\
							"Kalaallisut":"kal",\
							"Kannada":"kan",\
							"Kashmiri":"kas",\
							"Georgian":"kat",\
							"Kanuri":"kau",\
							"Kazakh":"kaz",\
							"Central Khmer":"khm",\
							"Kikuyu":"kik",\
							"Kinyarwanda":"kin",\
							"Kirghiz":"kir",\
							"Komi":"kom",\
							"Kongo":"kon",\
							"Korean":"kor",\
							"Kwanyama":"kua",\
							"Kurdish":"kur",\
							"Lao":"lao",\
							"Latin":"lat",\
							"Latvian":"lav",\
							"Limburgish":"lim",\
							"Lingala":"lin",\
							"Lithuanian":"lit",\
							"Luxembourgish":"ltz",\
							"Luba-Katanga":"lub",\
							"Ganda":"lug",\
							"Marshallese":"mah",\
							"Malayalam":"mal",\
							"Marathi":"mar",\
							"Macedonian":"mkd",\
							"Malagasy":"mlg",\
							"Maltese":"mlt",\
							"Mongolian":"mon",\
							"M?ori":"mri",\
							"Malay":"msa",\
							"Burmese":"mya",\
							"Nauru":"nau",\
							"Navajo":"nav",\
							"South Ndebele":"nbl",\
							"North Ndebele":"nde",\
							"Ndonga":"ndo",\
							"Nepali":"nep",\
							"Dutch Flemish":"nld",\
							"Norwegian Nynorsk":"nno",\
							"Norwegian Bokmal":"nob",\
							"Norwegian":"nor",\
							"Chichewa":"nya",\
							"Occitan ":"oci",\
							"Ojibwa":"oji",\
							"Oriya":"ori",\
							"Oromo":"orm",\
							"Ossetian":"oss",\
							"Panjabi":"pan",\
							"Pali":"pli",\
							"Polish":"pol",\
							"Portuguese":"por",\
							"Pashto":"pus",\
							"Quechua":"que",\
							"Romansh":"roh",\
							"Romanian":"ron",\
							"Rundi":"run",\
							"Russian":"rus",\
							"Sango":"sag",\
							"Sanskrit":"san",\
							"Sinhala":"sin",\
							"Slovak":"slk",\
							"Slovene":"slv",\
							"Northern Sami":"sme",\
							"Samoan":"smo",\
							"Shona":"sna",\
							"Sindhi":"snd",\
							"Somali":"som",\
							"Southern Sotho":"sot",\
							"Spanish":"spa",\
							"Albanian":"sqi",\
							"Sardinian":"srd",\
							"Serbian":"srp",\
							"Swati":"ssw",\
							"Sundanese":"sun",\
							"Swahili":"swa",\
							"Swedish":"swe",\
							"Tahitian":"tah",\
							"Tamil":"tam",\
							"Tatar":"tat",\
							"Telugu":"tel",\
							"Tajik":"tgk",\
							"Tagalog":"tgl",\
							"Thai":"tha",\
							"Tigrinya":"tir",\
							"Tonga":"ton",\
							"Tswana":"tsn",\
							"Tsonga":"tso",\
							"Turkmen":"tuk",\
							"Turkish":"tur",\
							"Twi":"twi",\
							"Uighur":"uig",\
							"Ukrainian":"ukr",\
							"Urdu":"urd",\
							"Uzbek":"uzb",\
							"Venda":"ven",\
							"Vietnamese":"vie",\
							"VolapŸk":"vol",\
							"Walloon":"wln",\
							"Wolof":"wol",\
							"Xhosa":"xho",\
							"Yiddish":"yid",\
							"Yoruba":"yor",\
							"Zhuang":"zha",\
							"Chinese":"zho",\
							"Zulu":"zul"}
			self.ListLanguages={}
			nnfin=len(Languages)
			Nn=0
			for nn in range (0,nnfin):
				LangExist = runBash("ls tessdata\\" \
							+ (Languages.values()[nn]) + ".traineddata")
				if LangExist :
					self.ListLanguages[Languages.keys()[nn]]=Languages.values()[nn]
					self.cmbLang.append_text(Languages.keys()[nn])
					if self.ConfVars["Language"] == Languages.values()[nn]:
						self.cmbLang.set_active(Nn)
					Nn = Nn + 1
	# f_create_lang END

	def f_lang_choice(self , widget): 
		global lang
		model = self.cmbLang.get_model()
		active = self.cmbLang.get_active()
		if active < 0:
			return None
		lang = self.ListLanguages[(model[active][0])]
		self.ConfVars["Language"]= lang + "\n"
		self.f_write_conf()
	# f_lang_coice END

	def f_read_conf(self):
		self.ConfVars={}
		try :
			Conff = open(self.Home+self.ConfFile, "r")
			lineas = Conff.readlines()
			nnfin = len(lineas)
			for nn in range(0,nnfin):
				if lineas[nn] == "\n": lineas[nn] = None
				if lineas[nn] :
					linea = lineas[nn].rstrip("\n")
					(Key,Value) = linea.split("=",1)
					self.ConfVars[Key] = Value
				nn = nn+1
			Conff.close() 
		except IOError:
			nn = 0
			self.ConfVars = {"Language":"eng" \
							, "Normalize":"True"}
			Conff = open(self.Home+self.ConfFile, "w")
			nnfin = len(self.ConfVars)
			for nn in range(0,nnfin):
				Par =  self.ConfVars.keys()[nn]+"="+self.ConfVars.values()[nn]
				Conff.write(Par+"\n")
				nn = nn+1
			Conff.write("\n")
			Conff.close()
		if "Normalize" not in self.ConfVars :
			self.ConfVars["Normalize"] = "True"

		if (self.ConfVars["Normalize"] == "True" \
						or self.ConfVars["Normalize"] == "Yes"):

			self.ConfVars["Normalize"] = "True"
			self.chkNormalize.set_active(True)
		else:
			self.chkNormalize.set_active(False)
	# f_read_conf END

	def f_write_conf(self):
		Conff = open(self.Home+self.ConfFile, "w")
		nnfin = len(self.ConfVars)
		for nn in range(0,nnfin):
			Par =  self.ConfVars.keys()[nn]+"="+self.ConfVars.values()[nn]
			Conff.write(Par+"\n")
			nn = nn+1
		Conff.close()
	# f_write_conf END


	class Dialogo:
		def create(self,Type,Data,Show):

			self.processdialog = gtk.Dialog("Processing",None\
					,gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK))
			self.processdialog.set_size_request(500,150)
			self.processdialog.show_now()

			self.hboxDialog = gtk.HBox(False,5)
			self.processdialog.vbox.pack_start(self.hboxDialog,False,False,1)
			self.hboxDialog.show_now()

			self.imgIcon=gtk.Image()
			if Type == "info" :
				self.imgIcon.set_from_file("share\\lime-ocr\\lime-ocr-logo.png")

			elif Type == "error" :
				self.imgIcon.set_from_file("share\\lime-ocr\\lime-ocr-error.png")
			self.hboxDialog.pack_start(self.imgIcon,False,False,1)
			self.imgIcon.show_now()

			self.lblProcessDialog = gtk.Label(Data)
			self.lblProcessDialog.show_now()

			self.hboxDialog.pack_start(self.lblProcessDialog , False, False, 1)
			self.lblProcessDialog.set_markup("")
			self.lblProcessDialog.show_now()

			self.processdialog.connect("response",self.destroy)
			self.processdialog.vbox.show_now()

			self.processdialog.show_all()

			if Show == "show":
				self.processdialog.action_area.show_now()
			elif Show == "hide":
				self.processdialog.action_area.hide()

		# f_create_dialog END

		def change(self,Type,Data,Show):

			if Type == "info" :
				self.imgIcon.set_from_file("share\\lime-ocr\\lime-ocr-logo.png")

			elif Type == "error" :
				self.imgIcon.set_from_file("share\\lime-ocr\\lime-ocr-error.png")
			self.imgIcon.show_now()

			if Data : self.lblProcessDialog.set_markup(Data)
			self.lblProcessDialog.show_now()

			if Show == "show":
				self.processdialog.action_area.show_now()
			elif Show == "hide":
				self.processdialog.action_area.hide()
		# f_dialog END
		
		def destroy(self,widget,Data):
			if Data == -5 or Data == "ok":
				self.processdialog.destroy()
				return "ok"
			else:
				self.processdialog.destroy()
				return "cancel"




		# f_dialog_destroy END

	### Process Options -------------------------
 	def f_opRotate(self,Nn):
		rotate_option = ""
		if (self.Images[Nn])[5] != 0: 
			rotate_option = "-rotate " + str((self.Images[Nn])[5])
		return rotate_option
	# f_opRotate END

	def f_opNormalize(self,Nn):	
		normalize_option = ""
		if (self.Images[Nn])[4] == True: normalize_option = "-normalize" 
		return normalize_option
	# f_opNormalize END

	def f_opCrop(self,Nn):
		crop_option = ""
		if ((self.Images[Nn])[6])[0]:
			rectangle = (((self.Images[Nn])[6])[0])
			x = str(rectangle.x)
			y = str(rectangle.y)
			w = str(rectangle.width)
			h = str(rectangle.height)
			crop_option = "-crop " + w + "x" + h + "+" + x + "+" + y
		return crop_option
	# f_crop_option END


	def f_concat_files(self, widget, Data):

		ConcatFiles=self.dlgConcat.get_filenames()
		Nombre = self.edtConcat.get_text()

		if Nombre :
			Nombre = "final_text"
		if ConcatFiles and Data == -5:
			Action = "cat "
			print Action
			nnfin = len(ConcatFiles)
			for nn in range(0,nnfin) :
				File = ConcatFiles[nn]
				Action = Action + " \"" + File + "\""
			CCfilename = self.btnConcat.set_current_folder(self.btnConcat.get_current_folder())
			print Action
			runBash(Action + " > \"" + self.FolderOut + Nombre + ".txt\"")
	# f_concat_files END

	def f_fronend_lang(self):
		# LFE = os.environ['LANG']
		LFE = "en_US.UTF-8"
		(LanCount,Codif) = LFE.rsplit(".",1)
		(Lang,Country) = LanCount.rsplit("_",1)
	
		if Lang == "es":
			self.LCselimg="Selección Imágenes"
			self.LCopen="Abrir"
			self.LCoutfolder="Carpeta de Destino"
			self.LCoutfoldertext="Seleccina una carpeta de destino"
			self.LCgeneralize="Generalizar"
			self.LCnormalize="Normalizar"
			self.LCcrop="Cortar"
			self.LCcroptext="Cliquea y arrastra para seleccionar un area"
			self.LCleft="Izq."
			self.LCright="Der."
			self.LCtop="Arriba"
			self.LCbottom="Abajo"
			self.LCrotate="Rotar"
			self.LCreset="Reajustar 0º"
			self.LCocr="OCR"
			self.LClanguage="Idioma"
			self.LCindextext="Indexado automático"
			self.LCstart="Inicio"
			self.LCstep="Salto"
			self.LCcolumn="Columna"
			self.LCall="Todas"
			self.LCselected="Seleccionda"
			self.LCimage="Imágen"
			self.LCtextfile="Archivo de Texto"
			self.LCrun="Procesar"
			self.LCprocess="Processando"
			self.LCprocessend="Reconocimiento de texto finalizado!"
			self.LCnameoffile="nombre_del_archivo"
			self.LCabort1="Proceso abortado.\nParece que ya se procesó:\n "
			self.LCconcat="Concatenar"
			self.LCconcattext="Crea un unico archivo de texto"
			self.LCseltxt="Selecciona archivos"
			self.LCconcatnom="Nombre Archivo"
			self.LCspsanish="Español"
			self.LCenglish="Inglés"
			self.LCdutch="Holandés"
			self.LCgerman="Alemán"
			self.LCfrench="Francés"
			self.LCitalian="Italiano"
			self.LCportuguese="Portugués"
		# elif Lang == "de":
		# elif Lang == "fr":
		# elif Lang == "pt":
		# elif Lang == "it":
		# elif Lang == "nl":
		else:
			self.LCselimg="Select Files"
			self.LCopen="Open"
			self.LCoutfolder="Output Folder"
			self.LCoutfoldertext="Select destination folder"
			self.LCgeneralize="Generalize"
			self.LCnormalize="Normalize"
			self.LCcrop="Crop"
			self.LCcroptext="Click and drop to select area"
			self.LCleft="Left"
			self.LCright="Right"
			self.LCtop="Top"
			self.LCbottom="Bottom"
			self.LCrotate="Rotate"
			self.LCreset="Reset 0º"
			self.LCocr="OCR"
			self.LClanguage="Language"
			self.LCindextext="Automatic page numbering"
			self.LCstart="Start"
			self.LCstep="Step"
			self.LCcolumn="Column"
			self.LCall="All"
			self.LCselected="Selected"
			self.LCimage="Image"
			self.LCtextfile="Text File"
			self.LCrun="Process"
			self.LCprocess="Processing"
			self.LCprocessend="Text Recogniton Finished!"
			self.LCnameoffile="name_of_file"
			self.LCabort1="Aborting process.\nIt seems it was yet processed.\nEither delete the file or save to some other loation\n"
			self.LCconcat="Concatenate"
			self.LCconcattext="Create only one file of text"
			self.LCseltxt="Select files"
			self.LCconcatnom="File Name"
			self.LCspsanish="Spanish"
			self.LCenglish="English"
			self.LCdutch="Dutch"
			self.LCgerman="German"
			self.LCfrench="French"
			self.LCitalian="Italian"
			self.LCportuguese="Portuguese"
			self.LChindi="Hindi"
			self.LCmalayalam="Malayalam"
			self.LCbangla="Bangla"
			self.LCbengali="Bengali"

	# f_frontend_lang END

	def destroy(self, widget, data=None):	# exit when main window closed
		gtk.main_quit()
	#}} destroy END

	def main(self):
		gtk.main()
	# main end
	# __init__ END
# Whc END 

# Funciones globales------------------------------------------------------------
def runBash(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	out = p.stdout.read().strip()
	return out
# runBash END

def runBash2(cmd):
	p2 = subprocess.Popen(cmd)
# runBash END

if __name__ == "__main__": 
	base = Whc()
	base.main()

