# Version 0.1 - 08/05/2024 - Initial Version, Copyright amirasf
# Version 0.2 - 15/05/2024 - Added argparse, Copyright amirasf

import pandas as pd
import json
import argparse
 

def create_a_splash_page(writer):
    
    # Creating a Splash page with instructions here

    workbook = writer.book
    worksheet = workbook.add_worksheet('Intro')

    # Increase the cell size of the merged cells to highlight the formatting.
    worksheet.set_column("B:I", 12)
    worksheet.set_row(3, 30)
    worksheet.set_row(6, 30)
    worksheet.set_row(7, 30)
    worksheet.set_row(10, 30)
    worksheet.set_row(11, 30)
    worksheet.set_row(12, 30)

    # Create a format to use in the merged range.
    merge_format_text = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#C0C0C0",
            'text_wrap': True,
            'font_size':12,
        }
    )

    merge_format_header = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#C0C0C0",
            'text_wrap': True,
            'font_size':16,
        }
    )

    worksheet.merge_range("B4:I4", "Cloud Foundations Accelerator Workbook", merge_format_header)

    worksheet.merge_range("B7:I8", "This is an automatically generated file (Source: CFA Lens GitHub Repo)", merge_format_text)

    worksheet.merge_range("B11:I13", "Use Tabs of this document below to work through CFA modules. Use Notes section for each action to document Customer-specific information or decisions ", merge_format_text)


def extract_url(additional_resources_list):
    
    # Helper function for parse_additional_resources_section() - it gets a list of dictionaries, extracts keys and merges them into a string

    resulting_url = ''
    for dictionary in additional_resources_list:
        content = dictionary.get('content', [])
        # Iterate through the 'content' list
        for item in content:
            display_text = item.get('displayText')
            url = item.get('url')
            resulting_url = display_text+' : '+url+'; '+resulting_url
    return resulting_url

def parse_additional_resources_section(pillar_data):

  # Sometimes we get multiple URLs and displaytext pairs in "Additional Resources" section - here we parse this list and do human-readable pairs by removing JSON-specific formatting
  # TODO implement URLs with text instead, but is tricky in pandas

  # Iterate through rows in the DataFrame
  for index, row in pillar_data.iterrows():
      # Check if 'Additional Resources' column is present and has values
      if 'Additional Resources' in row and row['Additional Resources'] and not type(row['Additional Resources']) == float:
          formatted_url = extract_url(row['Additional Resources'])
          pillar_data.at[index, 'Additional Resources'] = formatted_url
  return pillar_data

def format_excel(pillar_data,writer,sheet_name):

  # Mega-function for formatting Excel sheets we are creating from Pandas DataFrame
  
  workbook = writer.book
  worksheet = writer.sheets[sheet_name]

      

  # Find and merge 'Section' and 'Description' cells as they are identical for multiple Actions - basically, merging multiple rows

  section_format = workbook.add_format({'align': 'left', 'valign': 'vcenter','text_wrap': True, 'font_size':14, 'bold': True})
  description_format = workbook.add_format({'align': 'left', 'valign': 'vcenter','text_wrap': True})


  for section_name in pillar_data['Section'].unique():
      # find indices and add one to account for header
      u=pillar_data.loc[pillar_data['Section']==section_name].index.values + 1

      if len(u) <2: 
          pass # do not merge cells if there is only one Section name
      else:
          # merge cells using the first and last indices
          worksheet.merge_range(u[0], 0, u[-1], 0, pillar_data.loc[u[0],'Section'], section_format)

  for description in pillar_data['Description'].unique():
      # find indices and add one to account for header
      v=pillar_data.loc[pillar_data['Description']==description].index.values + 1

      if len(v) <2: 
          pass # do not merge cells if there is only one Description field
      else:
          # merge cells using the first and last indices
          worksheet.merge_range(v[0], 1, v[-1], 1, pillar_data.loc[v[0],'Description'], description_format)

  # ==== Creating multiple Format objects for headers, sections and 'normal' cells ===

  # create a 'normal cell' format and add it via set_column
  text_format = workbook.add_format({'text_wrap': True})

  # Get the dimensions of the dataframe.
  (max_row, max_col) = pillar_data.shape
  # Apply a conditional format to the required cell range.
  # All cells
  worksheet.set_column(1,max_col,100, text_format)
  # Section name
  worksheet.set_column(0,0,30, section_format)
  # Description section
  worksheet.set_column(1,1,100, description_format)
  # Action section (short)
  worksheet.set_column(2,2,30, text_format)
  # Checkbox section (even shorter)
  worksheet.set_column(3,3,10, text_format)


  # Add a header format and apply it.
  header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'font_size':16,
    'border': 1,
    'fg_color': '#C0C0C0'}
    )
  
  for col_num, value in enumerate(pillar_data.columns.values):
      worksheet.write(0, col_num, value, header_format)


def create_excel_sheets_nested(inputJSONfilename,excelfilename):

  # Main function - get JSON, parse it and create Excel sheet for each 'pillar' of CFA lens
  # We also do column renaming (as lens format has hardcoded values) and rearranging columns as Excel export does not follow order we want

  df = pd.read_json(inputJSONfilename)
  normalized_df = pd.json_normalize(df['pillars'])
  
  #print (normalized_df)
  
  writer = pd.ExcelWriter(excelfilename, engine='xlsxwriter')

  create_a_splash_page(writer)
               
  for index, row in normalized_df.iterrows():
        # Get the 'pillars' section for the current row
        pillar_name = row['name']
        #pillar_data = pd.DataFrame(row['questions'])

        pillar_data = pd.json_normalize(row['questions'], record_path=['choices'], meta = ['title', 'description'], record_prefix='_') 
        pillar_data.rename(columns={'_title': 'Topic or Action', 'title':'Section','description':'Description', '_helpfulResource.displayText': 'Detailed Guidance', '_additionalResources':'Additional Resources', '_helpfulResource.url': "Detailed Guidance URL"}, inplace=True)
        
        # Remove "None of These" choice rows as these are exported from WAFR tool - not relevant for a workbook.
        pillar_data = pillar_data[pillar_data["Topic or Action"].str.contains("None of these") == False]
  

        #Add Notes and Done (Checkbox) columns

        pillar_data['Done?'] = None
        pillar_data['Notes and Decisions'] = None

        #re-arranging columns
        if 'Additional Resources' in list(pillar_data.columns.values):
             pillar_data = pillar_data[['Section','Description','Topic or Action','Done?', 'Detailed Guidance','Detailed Guidance URL','Additional Resources', 'Notes and Decisions']]
             pillar_data = parse_additional_resources_section(pillar_data)
        else:
            pillar_data = pillar_data[['Section','Description','Topic or Action','Done?', 'Detailed Guidance', 'Detailed Guidance URL','Notes and Decisions']]
        

        # Write the DataFrame to the Excel file
        pillar_data.to_excel(writer, sheet_name=pillar_name, index=False)

        # invoke Excel formatting function                        
        format_excel(pillar_data, writer, sheet_name=pillar_name) 

        # Difficult to parse Additional Resources section, do it manually
        

        print(f"Excel sheet created for pillar {pillar_name}.")

  writer.close()

def main():
    
    parser = argparse.ArgumentParser(description='Use parameters below to convert WAFR Lens to an MS Excel file')
    parser.add_argument('-s', help='Source File', required=False, action='store')
    parser.add_argument('-d', help='Destination File', required=False, action='store')
    args = parser.parse_args()
    
    if not args.s or not args.d:
        parser.print_help()
        exit()
    create_excel_sheets_nested(args.s, args.d)

if __name__ == "__main__":
    main()

