'''input pictures output color information'''
from tools import *

#main function
if debug_mode == 1:
    #control progress
    if continue_run == 0 or not os.path.isfile(os.path.join(output_path, "progress.csv")):
        with open(os.path.join(output_path, "progress.csv"), 'w', newline = '') as f:
            writer = csv.writer(f)
            writer.writerow(["file", "status"])
            for file in os.listdir(data_path):
                writer.writerow([file, "not started"])
        if os.path.isfile(os.path.join(output_path, "color_sum.csv")):
            os.remove(os.path.join(output_path, "color_sum.csv"))
    #loop all files and check progress
    for file in os.listdir(data_path):
        progress = pd.read_csv(os.path.join(output_path, "progress.csv"), header = 0)
        if len(progress[progress["file"] == file]) == 0:
            progress.loc[len(progress)] = [file, 'not started']
        # =============================================================================
        #             if os.path.isfile(os.path.join(output_path, "s-" + file)):
        #                 file_status == "processing"
        #             else:
        #                 file_status == "not started"
        # =============================================================================
        file_status = progress[progress["file"] == file]["status"].values[0]

        if file_status == "processing":
            continue
        elif replace_outputs == 1 or file_status == "not started":
            progress["status"] = progress.apply(lambda row: "processing" if row["file"] == file else row["status"], axis = 1)
            progress.to_csv(os.path.join(output_path, "progress.csv"), index = False)
            #start to process the file
            time_it(file + " started")
            try:
                color_info = analyze_picture(file)
            except:
                continue
            if color_info is not None:
                with open(os.path.join(output_path, "color_sum.csv"), 'a+', newline = '') as f:
                    writer = csv.writer(f)
                    for row in color_info:
                        writer.writerow(row)
                time_it(file + " completed")
                #update status
                progress = pd.read_csv(os.path.join(output_path, "progress.csv"), header = 0)
                progress.loc[progress.index[progress['file'] == file], 'status'] = 'finished'
                progress.to_csv(os.path.join(output_path, "progress.csv"), index = False)
        else:
            continue

print("color analysis done!")

