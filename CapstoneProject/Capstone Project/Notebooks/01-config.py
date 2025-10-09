# Databricks notebook source
class Config():    
    def __init__(self):      
        # Updated to use Unity Catalog volumes
        self.base_dir_data = f"/Volumes/omar/sbit_db/capstone_data"
        self.base_dir_checkpoint = f"/Volumes/omar/sbit_db/capstone_checkpoints"
        self.db_name = "sbit_db"
        self.maxFilesPerTrigger = 1000
