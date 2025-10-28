from flask import Blueprint, request, render_template, redirect, flash, url_for, jsonify
from time import sleep
from shared import motors, csvWriter, daqHat, mainTest, distance
from config import IS_PI
from functions.database import Database
from utils.file_utils import create_html_tables



fake_pos = {"x": 0, "z": 0}

jog_bp = Blueprint('jog_bp', __name__)

# Create a Database instance
database = Database()

@jog_bp.route('/jog_mode', methods = ['POST', 'GET']) 
def jog_mode():
    global distance #, motors, csvWriter, mainTest, daqHat
    MACHINE_OPTIONS = ["MIDI", "EOS", "RENISHAW", "SLM"]
    PLATE_OPTIONS = [1, 2, 3]

    data_collection_names = database.get_data_collection_names() or []

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if IS_PI:
        motors.validate_position()  
          
    if request.method == 'POST':
        print("POST triggered!")
        print("Form keys:", list(request.form.keys()))
        print("Form data:", request.form.to_dict())  
        if request.form.get('jog_mode') == 'STOP':
            motors.running = False
            print("STOP triggered")
            return "Stopped", 200
        else:
            if (request.form.get('change_pulse') == "change"):
                distance = float(request.form.get('pulse_distance'))
                motors.pulse_distance = distance *200
            
            if request.form.get('coordinates') == "move_probes":
                motors.pulse_distance = 200 # Ensures distance is back to 1 millimeter
                final_x_pos = float(request.form.get('x_position'))
                final_z_pos = float(request.form.get('z_position'))
                
                if IS_PI:
                    motors.move_to_position('x', motors.x_position,final_x_pos)
                    motors.move_to_position('z', motors.z_position,final_z_pos)
                    motors.running = True
                    motors.pulse_distance = 200 *distance #Return the step size to previous value
                else:
                    fake_pos["x"] = final_x_pos
                    fake_pos["z"] = final_z_pos  
            
            #live motor position update without reload
            jog_cmd = request.form.get('jog_mode')
            if IS_PI and jog_cmd:
                if jog_cmd == 'Left': motors.joystick(0)
                elif jog_cmd == 'Right': motors.joystick(1)
                elif jog_cmd == 'Up': motors.joystick(2)
                elif jog_cmd == 'Down': motors.joystick(3)
                elif jog_cmd == 'Home': motors.reset()
                motors.running = True
            else:
                if jog_cmd == 'Left' or jog_cmd == 'Right':
                    fake_pos["x"] += 1
                elif jog_cmd == 'Up' or jog_cmd == 'Down':
                    fake_pos["z"] += 1

            if request.form.get('acq_data') == 'Calculate':
                samples = int(request.form.get('samples'))
                rate = int(request.form.get('frequency'))
                iteration = int(request.form.get('iteration'))
                fileName = request.form.get('fileName')
                selected_machine = request.form.get('machine')
                selected_plate = request.form.get('plate') 

                csvWriter.machine = selected_machine
                csvWriter.plate = selected_plate



                database.overwrite(csvWriter.fileName)
                csvWriter.setFileName(fileName, selected_machine, selected_plate,True,1)

                full_fileName = csvWriter.fileName
                if not hasattr(daqHat,'Eo2'):
                    flash('Please enter velocity parameters before beginning')
                    return redirect(url_for('main_page'))
                mainTest.multipleSample(samples,rate, iteration,selected_machine,selected_plate)

                data_table, raw_data_table, con_data_table = create_html_tables(1,fileName)

                PS_data_table = create_html_tables(5,full_fileName)
                #The graph is rendered at data_page.html
                return render_template('data_page.html',PS_data=PS_data_table,data=data_table,raw_data=raw_data_table,con_data=con_data_table,usePointSampleGraph=True,iteration=iteration)
            

    if is_ajax:
        print("In Ajax")
        print("[RETURNING POS]", motors.x_position, motors.z_position)
        return jsonify(
                x_pos=round(motors.x_position, 2) if IS_PI else fake_pos["x"],
                z_pos=round(motors.z_position, 2) if IS_PI else fake_pos["z"]
        )  
    return render_template('jog_mode.html', x_pos = motors.x_position, z_pos = motors.z_position,machine=MACHINE_OPTIONS, plate=PLATE_OPTIONS)
