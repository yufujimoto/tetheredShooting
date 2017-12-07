#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import general libraries.
import sys, os, uuid, shutil, time, math, tempfile, logging, pyexiv2, datetime

# Import the library for acquiring file information.
from stat import *

# Import PyQt5 libraries for generating the GUI application.
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread, pyqtSignal

# Import general operations.
import modules.general as general

# Import camera and image processing library.
import modules.imageProcessing as imageProcessing
import dialog.checkTetheredImageDialog as checkTetheredImageDialog

class CheckImageDialog(QDialog, checkTetheredImageDialog.Ui_tetheredDialog):
    def __init__(self, parent=None, path=None):
        # Set the source directory which this program located.
        self._source_directory = parent.source_directory
        self._icon_directory = parent.icon_directory
        self._qt_image = parent.qt_image
        self._image_extensions = parent.image_extensions
        self._raw_image_extensions = parent.raw_image_extensions
        self._sound_extensions = parent.sound_extensions
        
        super(CheckImageDialog, self).__init__(parent)
        self.setupUi(self)
        
        # Initialize the window.
        self.setWindowTitle(self.tr("Check Tethered Image"))
        self.setWindowState(Qt.WindowMaximized)
        
        # Get the path of the tethered image.
        self.tethered = path
        
        # Define the return values.
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Initialyze the image panel.
        self.image_panel.resize(800, 600)
        self.image_panel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        # Initialyze the image info view.
        self.tre_img_info.setMaximumSize(QSize(300, 16777215))
        
        # Initialyze the file information view.
        self.lst_fls.setMaximumSize(QSize(16777215, 100))
        self.lst_fls.itemSelectionChanged.connect(self.getImageFileInfo)
        
        # Get tethered image files.
        self.getImageFiles()
        
    # Properties for default paths.
    @property
    def source_directory(self): return self._source_directory
    @property
    def siggraph_directory(self): return self._siggraph_directory
    @property
    def icon_directory(self): return self._icon_directory
    @property
    def temporal_directory(self): return self._temporal_directory
    @property
    def root_directory(self): return self._root_directory
    @property
    def table_directory(self): return self._table_directory
    @property
    def consolidation_directory(self): return self._consolidation_directory
    @property
    def database(self): return self._database
    
    # Properties for default labels.
    @property
    def label_consolidation(self): return self._label_consolidation
    @property
    def label_material(self): return self._label_material
    
    # Properties for default extensions.
    @property
    def qt_image(self): return self._qt_image
    @property
    def image_extensions(self): return self._image_extensions
    @property
    def raw_image_extensions(self): return self._raw_image_extensions
    @property
    def sound_extensions(self): return self._sound_extensions
    
    # Setter for default paths.
    @source_directory.setter
    def source_directory(self, value): self._source_directory = value
    @siggraph_directory.setter
    def siggraph_directory(self, value): self._siggraph_directory = value
    @icon_directory.setter
    def icon_directory(self, value): self._icon_directory = value
    @temporal_directory.setter
    def temporal_directory(self, value): self._temporal_directory = value
    @root_directory.setter
    def root_directory(self, value): self._root_directory = value
    @table_directory.setter
    def table_directory(self, value): self._table_directory = value
    @consolidation_directory.setter
    def consolidation_directory(self, value): self._consolidation_directory = value
    @database.setter
    def database(self, value): self._database = value
    
    # Setter for default labels.
    @label_consolidation.setter
    def label_consolidation(self, value): self._label_consolidation = value
    @label_material.setter
    def label_material(self, value): self._label_material = value
    
    # Setter for default extensions.
    @qt_image.setter
    def qt_image(self, value): self._qt_image = value
    @image_extensions.setter
    def image_extensions(self, value): self._image_extensions = value
    @raw_image_extensions.setter
    def raw_image_extensions(self, value): self._raw_image_extensions = value
    @sound_extensions.setter
    def sound_extensions(self, value): self._sound_extensions = value
    
    def getImageFiles(self):
        print("CheckImageDialog::getImageFiles(self)")
        
        try:
            # Get the file list with given path.
            img_lst_main = general.getFilesWithExtensionList(self.tethered, self._image_extensions)
            img_lst_raw = general.getFilesWithExtensionList(self.tethered, self._raw_image_extensions)
            
            # Add each image file name to the list box.
            if img_lst_main > 0:
                for img_main in img_lst_main:
                    img_item = QListWidgetItem(img_main)
                    self.lst_fls.addItem(img_item)
                    
            # Add each RAW file name to the list box.
            if img_lst_raw > 0:
                for img_raw in img_lst_raw:
                    img_item = QListWidgetItem(img_raw)
                    self.lst_fls.addItem(img_raw)
        except Exception as e:
            print("Error occurs in CheckImageDialog::getImageFiles(self)")
            print(str(e))
    
    def getImageFileInfo(self):
        print("CheckImageDialog::getImageFileInfo(self)")
        
        try:
            # Get the path to the image directory of the tethered imagesw
            img_path = self.tethered
            
            # Get the tree view for the metadata of consolidation.
            tre_fl = self.tre_img_info
            
            # Get the selected image file.
            lst_fls = self.lst_fls.currentItem().text()
            
            # Get the file name which is currently selected.
            img_file_name = lst_fls
            
            # Make the full path of the selected image file.
            img_file_path = os.path.join(img_path,img_file_name)
            
            if os.path.exists(img_file_path):
                # Clear the image file information.
                tre_fl.clear()
                
                # Get file information by using "dcraw" library.
                img_stat = imageProcessing.getMetaInfo(img_file_path).strip().split("\n")
                
                # Get each metadata entry.
                for entry in img_stat:
                    # Split metadata entry by ":".
                    entry_line = entry.split(":")
                    
                    # Get the metadata key.
                    entry_key = entry_line[0]
                    
                    # Get the metadata value.
                    entry_val = entry_line[1]
                    
                    # Add file information to the tree list.
                    tre_fl.addTopLevelItem(QTreeWidgetItem([entry_key, entry_val]))
                
                # Get file information by using python "stat" library.
                fl_stat = os.stat(img_file_path)
                
                # Get file size.
                fl_size = str(round(float(fl_stat[ST_SIZE]/1000),3))+"KB"
                
                # Get time for last access, modified and creat.
                fl_time_last = time.asctime(time.localtime(fl_stat[ST_ATIME]))
                fl_time_mod = time.asctime(time.localtime(fl_stat[ST_MTIME]))
                fl_time_cre = time.asctime(time.localtime(fl_stat[ST_CTIME]))
                
                # Add file information to the tree list.
                tre_fl.addTopLevelItem(QTreeWidgetItem(["Created", fl_time_cre]))
                tre_fl.addTopLevelItem(QTreeWidgetItem(["Last Modified", fl_time_mod]))
                tre_fl.addTopLevelItem(QTreeWidgetItem(["Last Access", fl_time_last]))
                tre_fl.addTopLevelItem(QTreeWidgetItem(["File Size", fl_size]))
                
                # Refresh the tree view.
                tre_fl.show()
                self.showImage()
            else:
                # Deselect the item.
                tre_fl.clearSelection()
                tre_fl.clear()
        except Exception as e:
            print("Error occurs in CheckImageDialog::getImageFileInfo(self)")
            print(str(e))
            
    def showImage(self):
        print("CheckImageDialog::showImage(self)")
        
        try:
            panel_w = self.image_panel.width()
            panel_h = self.image_panel.height()
            
            if not self.lst_fls.currentItem() == None:
                # Get the file name and its path.
                img_file_name = self.lst_fls.currentItem().text()
                img_path = os.path.join(self.tethered, img_file_name)
                
                # Check the image file can be displayed directry.
                img_base, img_ext = os.path.splitext(img_file_name)
                img_valid = False
                
                for qt_ext in self._qt_image:
                    # Exit loop if extension is matched with Qt supported image.
                    if img_ext.lower() == qt_ext.lower():
                        img_valid = True
                        break
                
                # Check whether the image is Raw image or not.
                if not img_valid == True:
                    # Extract the thumbnail image from the RAW image by using "dcraw".
                    imageProcessing.getThumbnail(img_path)
                    
                    # Get the extracted thumbnail image.
                    img_file_name = img_base + ".thumb.jpg"
                    
                    # Get the full path of the thumbnail image.
                    img_path = os.path.join(self.tethered, img_file_name)
                
                if os.path.exists(img_path):
                    # Create the container for displaying the image
                    org_pixmap = QPixmap(img_path)
                    scl_pixmap = org_pixmap.scaled(panel_w, panel_h, Qt.KeepAspectRatio)
                    
                    # Set the image file to the image view container.
                    self.image_panel.setPixmap(scl_pixmap)
                    
                    # Show the selected image.
                    self.image_panel.show()
                else:
                    # Create error messages.
                    error_title = "エラーが発生しました"
                    error_msg = "このファイルはプレビューに対応していません。"
                    error_info = "諦めてください。RAW + JPEG で撮影することをお勧めします。"
                    error_icon = QMessageBox.Critical
                    error_detailed = str(e)
                    
                    # Handle error.
                    general.alert(title=error_title, message=error_msg, icon=error_icon, info=error_info, detailed=error_detailed)
                    
                    # Returns nothing.
                    return(None)
            else:
                return(None)
        except Exception as e:
                print("Error occurs in CheckImageDialog::showImage(self)")
                print(str(e))