from flask import Flask, render_template, request, jsonify
from model.main.scrap import search_google_business, save_to_csv
from model.main.clean import clean_csv_files
from model.main.visit import process_csv_files
import os

app = Flask(__name__, template_folder='model/template')

input_dir = 'model/output/raw-output'
final_output_dir = 'model/output/final-output'
def get_abs_path(path):
    return os.path.join(os.path.dirname(__file__), path)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_query = request.form.get("search_query")

        try:
            if not search_query:
                return jsonify({"status": "error", "message": "Search query is required."})

            # Step 1: Scrape data based on search query
            all_data = search_google_business(search_query)
            if not all_data:
                return jsonify({"status": "error", "message": "No results found."})

            # Step 2: Save the scraped data to CSV
            raw_csv_path = get_abs_path(f"model/output/raw-output/{search_query}.csv")
            save_to_csv(all_data, raw_csv_path)

            # Step 3: Ensure the file exists before proceeding
            if not os.path.exists(raw_csv_path):
                return jsonify({"status": "error", "message": f"File {raw_csv_path} not found after saving."})

            # Step 4: Clean the raw CSV files
            clean_output_dir = get_abs_path('model/output/clean-output')
            clean_csv_files(get_abs_path('model/output/raw-output'), clean_output_dir)

            # Ensure that cleaned CSV files exist
            cleaned_files = os.listdir(clean_output_dir)
            if not cleaned_files:
                return jsonify({"status": "error", "message": "No cleaned CSV files found."})

            # Debugging output to check cleaned files
            print(f"Cleaned files: {cleaned_files}")

            # Step 5: Process the cleaned CSV files (extract emails, etc.)
            process_csv_files()

            return jsonify({"status": "success", "message": f"Data scraped, saved, cleaned, and processed for {search_query}.csv"})

        except Exception as e:
            return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

    return render_template("index.html")


# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         search_query = request.form.get("search_query")

#         try:
#             if not search_query:
#                 return jsonify({"status": "error", "message": "Search query is required."})     
#             all_data = search_google_business(search_query)
#             if not all_data:
#                 return jsonify({"status": "error", "message": "No results found."})

#             raw_csv_path = get_abs_path(f"model/output/raw-output/{search_query}.csv")
#             save_to_csv(all_data, raw_csv_path)

#             if not os.path.exists(raw_csv_path):
#                 return jsonify({"status": "error", "message": f"File {raw_csv_path} not found after saving."})
            
#             # Clean csv files
#             clean_output_dir = get_abs_path('model/output/clean-output')
#             clean_csv_files(get_abs_path('model/output/raw-output'), clean_output_dir)

#             cleaned_files = os.listdir(clean_output_dir)
#             if not cleaned_files:
#                 return jsonify({"status": "error", "message": "No cleaned CSV files found."})
#             print(f"Cleaned files: {cleaned_files}")

#             # Step 5: Process the cleaned CSV files (extract emails, etc.)
#             process_csv_files(input_dir, final_output_dir)

#             return jsonify({"status": "success", "message": f"Data scraped, saved, cleaned, and processed for {search_query}.csv"})

#         except Exception as e:
#             return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

#     return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)



# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         search_query = request.form.get("search_query")

#         try:
#             if not search_query:
#                 return jsonify({"status": "error", "message": "Search query is required."})

#             # Step 1: Scrape data based on search query
#             all_data = search_google_business(search_query)
#             if not all_data:
#                 return jsonify({"status": "error", "message": "No results found."})

#             # Step 2: Save the scraped data to CSV
#             raw_csv_path = get_abs_path(f"model/output/raw-output/{search_query}.csv")
#             save_to_csv(all_data, raw_csv_path)

#             # Step 3: Ensure the file exists before proceeding
#             if not os.path.exists(raw_csv_path):
#                 return jsonify({"status": "error", "message": f"File {raw_csv_path} not found after saving."})

#             # Step 4: Clean the raw CSV files
#             clean_output_dir = get_abs_path('model/output/clean-output')
#             clean_csv_files(get_abs_path('model/output/raw-output'), clean_output_dir)

#             # Ensure that cleaned CSV files exist
#             cleaned_files = os.listdir(clean_output_dir)
#             if not cleaned_files:
#                 return jsonify({"status": "error", "message": "No cleaned CSV files found."})

#             # Debugging output to check cleaned files
#             print(f"Cleaned files: {cleaned_files}")

#             # Step 5: Process the cleaned CSV files (extract emails, etc.)
#             process_csv_files()

#             return jsonify({"status": "success", "message": f"Data scraped, saved, cleaned, and processed for {search_query}.csv"})

#         except Exception as e:
#             return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

#     return render_template("index.html")
