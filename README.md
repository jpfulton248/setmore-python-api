## Unofficial Setmore API ##

#Initialize with:#
```sm_auth = SetmoreAuth()
sm = Setmore(sm_auth)```

#Generate json files for service and staff list with:#
Default value for save is False. To save the json files so other methods can reference them, set save=True. File location default is 'credentials/staff.json'.
```def get_all_staff(self, save=True, file='credentials/staff.json')```