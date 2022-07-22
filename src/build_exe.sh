#! /bin/bash
pyinstaller --noconfirm --onefile --console --name "ViolationTool" \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/dataframes:dataframes/" \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/images:images/" \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/guis:guis/" \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/assets:assets" \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/info.py:." \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/utilities.py:." \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/nursing_homes.py:." \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/long_term_care.py:." \
--add-data "/Users/Freddie/Impruvon/ViolationToolv2/src/home_health_care.py:." \
"/Users/Freddie/Impruvon/ViolationToolv2/src/guis/gui.py"