from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from .models import Product, HealthTip, ProductCategory, HealthTipCategory
from .serializers import ProductSerializer
import json
import magic
import pandas as pd
import numpy as np


# ---------------Product section------------------#
"""
    This section contain all view functions for the Product database
"""


def retrieve_products():
    # retrieve the products in the database
    # this must be done before displaying the admin page
    
    products = Product.objects.all()
    return products      


@login_required(login_url='/product/user/login')
def view_admin(request):
    # display the products in the database on a homepage
    
    if Product.objects.exists():
        products = retrieve_products()
        return render(request, 'products/index.html',
                    {'products': products})
    else:
        return render(request, 'products/index.html',
                      {'msg': 'No product has been added'})


@login_required(login_url='/product/user/login')
def add_product(request):
    # add new product to the database

    if request.method == 'POST':
        try:
            # ensure the selected file is image format
            allowed_formats = ['image/png', 'image/jpeg', 'image/jpg']
            image_file = request.FILES['image']
            file_type = magic.from_buffer(image_file.read(), mime=True)
            if file_type not in allowed_formats:
                return render(request, 'products/new_product.html',
                            {'msg': 'File must be image format.'})
            else:
                # Save the uploaded file since it's an image format
                new_product = Product()
                # ensure the record does not exist in the database
                name = request.POST['name']
                brand = request.POST['brand']
                if Product.objects.filter(name__iexact=name, brand__iexact=brand).exists():
                    return render(request, 'products/new_product.html',
                                {'msg': 'product already exist.'})
                else:
                    new_product.name = request.POST['name']
                    new_product.img = request.FILES['image']
                    new_product.brand = request.POST['brand']
                    new_product.price = request.POST['price']
                    new_product.category = request.POST['category']
                    new_product.unit_code = request.POST['unit_code']
                    new_product.comment = request.POST['comment']
                    new_product.save()
                    
                    # save the category if its a new category
                    if ProductCategory.objects.filter(name__iexact=request.POST['category']).exists():
                        pass
                    else:
                        category = ProductCategory()
                        category.name = request.POST['category']
                        category.save()
                    return render(request, 'products/new_product.html',
                                {'msg': 'product added successfully!.'})       
        except ValidationError:
            return render(request, 'products/new_product.html',
                        {'msg': 'one or more entries not valid.'}) 
    else:    
        return render(request, 'products/new_product.html')
    

@login_required(login_url='/product/user/login')
def del_all_products(request):
    # delete all products in the database

    if Product.objects.exists():
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        return render(request, 'products/index.html',
                      {'msg': 'All products deleted successfully.'})
    else:
        return render(request, 'products/index.html', {'msg': 'No record exist.'})
    

def clean_database(table):
    # pre-processing of data before uploading

    COLUMN = [['Name', 'Price', 'Category', 'Unit-Code', 'Brand']]
    

    column_names = list(table.columns)
    for item in column_names:
        
        # ensure the column names are correct: 
        # no whitespace and not case sensitive
        # strip all records in the columns
        if str(item).strip().upper() == 'NAME':
            # strip all records in 'name' column
            stripped_column = table[item].str.strip()
            table[item] = stripped_column

            # make the first letter of words uppercase in 'name' column
            capitalize_column = table[item].str.title()
            table[item] = capitalize_column
            
            # sort the table using the 'name' column
            table = table.sort_values(item).reset_index(drop=True)
            table.dropna(how='all', inplace=True)
            table.rename(columns={item: 'Name'}, inplace=True)
        elif str(item).strip().upper() == 'BRAND': 
            stripped_column = table[item].str.strip()
            table[item] = stripped_column

            # make the first letter of words uppercase in 'brand' column
            capitalize_column = table[item].str.title()
            table[item] = capitalize_column

            table.rename(columns={item: 'Brand'}, inplace=True)
        elif str(item).strip().upper() == 'CATEGORY': 
            stripped_column = table[item].str.strip()
            table[item] = stripped_column
            table.rename(columns={item: 'Category'}, inplace=True)   
        elif str(item).strip().upper() == 'UNIT-CODE': 
            stripped_column = table[item].str.strip()
            table[item] = stripped_column
            table.rename(columns={item: 'Unit_code'}, inplace=True) 
        elif str(item).strip().upper() == 'PRICE':
            table.rename(columns={item: 'Price'}, inplace=True)
            # convert every non numeric value in price column to NaN
            table.loc[table['Price'].str.isnumeric() == False,['Price']] = np.nan              
        else:
            pass

    # ensure there are no empty cells
    rows_with_emptycells = table[table.isna().any(axis=1)]
    table.dropna(subset=['Name', 'Brand', 'Price', 'Category', 'Unit_code'],
                  inplace=True, ignore_index=True)
    
    return table, rows_with_emptycells


def clear_duplicates(table):
    # remove all duplicates (same name and brand), and store the deleted rows in another table

    duplicates = table[table.duplicated(subset=['Name', 'Brand']) == True]
    table.drop_duplicates(subset=['Name', 'Brand'], inplace=True, ignore_index=True)

    return table, duplicates    


@login_required(login_url='/product/user/login')
def import_products(request):
    # import products from excel spreadsheet into the database


    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        # ensure the selected file is excel format
        try:
            # Load the Excel file into a DataFrame
            df = pd.read_excel(excel_file)
            
            # data preprocessing actions (first action)
            results = clean_database(df)
            preprocessed_table = results[0]
            invalid_rows = results[1]
            # data preprocessing actions (second action)
            final_results = clear_duplicates(preprocessed_table)
            preprocessed_table = final_results[0]
            duplicate_rows = final_results[1]
            
            # Iterate over each row in the DataFrame and create model instances
            line_number = 0
            no_of_saved_products = 0

            # create a dataframe to store imported products that are already in the database 
            already_existing_rows = pd.DataFrame({'Name': [], 'Brand': []})
            

            for row in preprocessed_table.itertuples():
                # Access the column values using row.'column_name'
                # Create an instance of your model and save it
                
                line_number += 1
                if Product.objects.filter(name__iexact=str(row.Name), brand__iexact=str(row.Brand)).exists():
                    # check if product is already in the database
                    repeated_row = pd.DataFrame([[str(row.Name), str(row.Brand)]], columns=['Name', 'Brand'])
                    already_existing_rows = pd.concat([already_existing_rows, repeated_row], ignore_index=True)
                else:  
                    try:    
                        product = Product()
                        product.name = str(row.Name)
                        product.brand = str(row.Brand)
                        product.price = str(row.Price)
                        product.unit_code = str(row.Unit_code)
                        product.category = str(row.Category)

                        product.save()
                        no_of_saved_products += 1

                        # save the category if its a new category
                        if ProductCategory.objects.filter(name__iexact=str(row.Category)).exists():
                            pass
                        else:
                            category = ProductCategory()
                            category.name = request.POST['category']
                            category.save()
                        
                    #print('true')
                    except ValueError:
                         return render(request, 'products/index.html',
                        {'msg': f'Invalid entry{str(row.Name)},{str(row.Brand)}.'})

            #convert the dataframes to dictionary so it can be stored in the session
            request.session['rows_invalid'] = invalid_rows.to_dict(orient='records')
            request.session['rows_duplicates'] = duplicate_rows.to_dict(orient='records')
            request.session['rows_existing'] = already_existing_rows.to_dict(orient='records')

        except ValueError:
            return render(request, 'products/index.html',
                        {'msg': 'Invalid format. File must be .xls,.xlsx format.'})
        except AttributeError:
            return render(request, 'products/index.html',
                        {'msg': 'Unsuccessful.column not found,please check your column names.'})
        except ValidationError:
            return render(request, 'products/index.html',
                        {'msg': f'Invalid entry(data type not accepted).line number {line_number}'}) 

         # display a success message
        if len(invalid_rows) != 0 or len(duplicate_rows) != 0 or len(already_existing_rows) != 0:
            print(len(invalid_rows))
            print(len(duplicate_rows))
            print(len(already_existing_rows))
            no_of_invalidrows = len(invalid_rows) + len(duplicate_rows) + len(already_existing_rows)
            products = retrieve_products()
            return render(request, 'products/index.html',
                    {'msg': f'{no_of_saved_products} Products successfully imported!.',
                        'alert': 'some products could not be added',
                        'num': no_of_invalidrows, "no_saved": no_of_saved_products,
                        'products': products})
        else:
            products = retrieve_products()
            return render(request, 'products/index.html',
                    {'msg': 'All Products successfully imported!.',
                     'products': products})
    else:
        return redirect('view_admin')
    

@login_required(login_url='/product/user/login')
def show_invalid_rows(request):
    # show invalid rows

    empty_rows = request.session['rows_invalid']
    duplicate_rows = request.session['rows_duplicates']
    existing_rows = request.session['rows_existing']

    return render(request, 'products/invalid.html',
                  {'empty_rows': empty_rows, 
                   'duplicate_rows': duplicate_rows,
                   'existing_rows': existing_rows})


@login_required(login_url='/product/user/login')
def export_products(request):
    # export products in the database to excel sheet

    if Product.objects.exists():
        # check if there is a product in the database before exporting
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        data = json.dumps(serializer.data)
        data_frame = pd.read_json(data)

        # Create an Excel writer using pandas 
        data_frame.to_excel('media/xlsx/myfile.xlsx', index=False, sheet_name='Sheet1')

        # Define the file path and URL
        file_path = 'myfile.xlsx'
        file_url = '/media/xlsx/' + file_path

        products = retrieve_products()
        return render(request, 'products/index.html', 
                    {'excel_url': file_url,
                    'msg': 'Products exported successfully',
                    'exported': True, 'products': products
                    })
    else:
        return render(request, 'products/index.html', 
                      {'msg': 'No product to export',
                       })
    

@login_required(login_url='/product/user/login')
def product_details(request, pk):
    # display the product details selected by the user

    try:
        product = Product.objects.get(pk=pk)

        return render(request, 'products/product_details.html',
                      {'product': product})
    except ObjectDoesNotExist:
        return render(request, 'products/index.html',
                      {'msg': "product does not exist"})
    

@login_required(login_url='/product/user/login')
def edit_product(request, pk):
    # edit the details of the product

    if request.method == 'POST':
        product = Product.objects.get(pk=pk)

        # ensure the selected file is image format
        allowed_formats = ['image/png', 'image/jpeg', 'image/jpg']
        try:
            image_file = request.FILES['image']
            file_type = magic.from_buffer(image_file.read(), mime=True)
            if file_type not in allowed_formats:
                products = retrieve_products()
                return render(request, 'products/index.html',
                            {'msg': 'changes not saved.uploaded file must be image format.',
                            'products': products})
            else:
                product.name = request.POST['name']
                product.img = request.FILES['image']
                product.brand = request.POST['brand']
                product.category = request.POST['category']
                product.price = request.POST['price']
                product.unit_code = request.POST['unit_code']
                product.comment = request.POST['comment']

                product.save()
                # save the category if its a new category
                if ProductCategory.objects.filter(name__iexact=request.POST['category']).exists():
                    pass
                else:
                    category = ProductCategory()
                    category.name = request.POST['category']
                    category.save()
                products = retrieve_products()
                return render(request, 'products/index.html',
                            {'msg': 'Product edited successfully!',
                            'products': products})
        except MultiValueDictKeyError:
            try:
                product.name = request.POST['name']
                product.brand = request.POST['brand']
                product.category = request.POST['category']
                product.price = request.POST['price']
                product.unit_code = request.POST['unit_code']
                product.comment = request.POST['comment']

                product.save()
                # save the category if its a new category
                if ProductCategory.objects.filter(name__iexact=request.POST['category']).exists():
                    pass
                else:
                    category = ProductCategory()
                    category.name = request.POST['category']
                    category.save()
                products = retrieve_products()
                return render(request, 'products/index.html',
                            {'msg': 'Product edited successfully!',
                            'products': products}) 
            except ValidationError:
                return render(request, 'products/index.html',
                          {'msg': 'maximum number of characters exceeded for name/brand/category/price or unit code'})   
        except ValidationError:
            return render(request, 'products/index.html',
                          {'msg': 'maximum number of characters exceeded for name/brand/category/price or unit code'})   
    else:
        return redirect('view_admin')
    

@login_required(login_url='/product/user/login')
def delete_product(request, pk):
    # delete the product from database

    if request.method == 'POST':
        product = Product.objects.get(pk=pk)
        name = product.name
        brand = product.brand
        product.delete() 

        products = retrieve_products()
        return render(request, 'products/index.html',
                      {'msg': f'{name} - {brand} deleted successfully!.',
                       'products': products})
    else:
        return redirect('view_admin')
    

# ---------------HealthTips section------------------#
"""
    This section contain all view functions for the HealthTips database
"""


@login_required(login_url='/product/user/login')
def add_tips(request):
    # add new health tip to the database

    if request.method == 'POST':
        try:
            # ensure the selected file is image format
            allowed_formats = ['image/png', 'image/jpeg', 'image/jpg']
            image_file = request.FILES['image']
            file_type = magic.from_buffer(image_file.read(), mime=True)
            if file_type not in allowed_formats:
                return render(request, 'Tips/new_tip.html',
                            {'msg': 'File must be image format.'})
            else:
                # Save the uploaded file since it's an image format
                new_tip = HealthTip()
                # ensure the record does not exist in the database
                title = request.POST['title']
                if HealthTip.objects.filter(title__iexact=title).exists():
                    return render(request, 'Tips/new_tip.html',
                                {'msg': 'Health tip already exist.'})
                else:
                    new_tip.title = request.POST['title']
                    new_tip.img = request.FILES['image']
                    new_tip.category = request.POST['category']
                    new_tip.content = request.POST['content']
                    new_tip.save()
                    # save the category if its a new category
                    if HealthTipCategory.objects.filter(name__iexact=request.POST['category']).exists():
                        pass
                    else:
                        category = HealthTipCategory()
                        category.name = request.POST['category']
                        category.save()
                    return render(request, 'Tips/new_tip.html',
                                {'msg': 'Health tip added successfully!.'})   
                    
        except ValidationError:
            return render(request, 'Tips/new_tip.html',
                        {'msg': 'one or more entries not valid.'}) 
    else:    
        return render(request, 'Tips/new_tip.html')
    

@login_required(login_url='/product/user/login')
def show_all_tips(request):
    # show all the tips

    if HealthTip.objects.exists():
        tips = HealthTip.objects.all()
        return render(request, 'Tips/show_tips.html', 
                      {'tips': tips})
    else:

        return render(request, 'Tips/show_tips.html',
                      {'msg': 'No tip has been added.'})


@login_required(login_url='/product/user/login')
def tip_details(request, pk):
    # display the health tip details selected by the user

    try:
        tip = HealthTip.objects.get(pk=pk)

        return render(request, 'Tips/tip_details.html',
                      {'tip': tip})
    except ObjectDoesNotExist:
        return render(request, 'Tips/show_tips.html',
                      {'msg': "Health Tip does not exist"})


@login_required(login_url='/product/user/login')
def del_all_tips(request):
    # delete all health tips in the database

    if HealthTip.objects.exists():
        HealthTip.objects.all().delete()
        HealthTipCategory.objects.all().delete()
        return render(request, 'Tips/show_tips.html',
                      {'msg': 'All Health Tips deleted successfully.'})
    else:
        return render(request, 'Tips/show_tips.html', {'msg': 'No record exist.'})
    

@login_required(login_url='/product/user/login')
def edit_tip(request, pk):
    # edit the details of the health tip

    if request.method == 'POST':
        tip = HealthTip.objects.get(pk=pk)

        # ensure the selected file is image format
        allowed_formats = ['image/png', 'image/jpeg', 'image/jpg']
        try:
            image_file = request.FILES['image']
            file_type = magic.from_buffer(image_file.read(), mime=True)
            if file_type not in allowed_formats:
                tips = HealthTip.objects.all()
                return render(request, 'Tips/show_tips.html',
                            {'msg': 'changes not saved.uploaded file must be image format.',
                            'tips': tips})
            else:
                tip.title = request.POST['title']
                tip.img = request.FILES['image']
                tip.category = request.POST['category']
                tip.content = request.POST['content']

                tip.save()
                # save the category if its a new category
                if HealthTipCategory.objects.filter(name__iexact=request.POST['category']).exists():
                    pass
                else:
                    category = HealthTipCategory()
                    category.name = request.POST['category']
                    category.save()
                tips = HealthTip.objects.all()
                return render(request, 'Tips/show_tips.html',
                            {'msg': 'Health tip edited successfully!',
                            'tips': tips})
        except MultiValueDictKeyError:
            try:
                tip.title = request.POST['title']
                tip.category = request.POST['category']
                tip.content = request.POST['content']

                tip.save()
                # save the category if its a new category
                if HealthTipCategory.objects.filter(name__iexact=request.POST['category']).exists():
                    pass
                else:
                    category = HealthTipCategory()
                    category.name = request.POST['category']
                    category.save()
                tips = HealthTip.objects.all()
                return render(request, 'Tips/show_tips.html',
                            {'msg': 'Health tip edited successfully!',
                            'tips': tips})
            except ValidationError:
                 return render(request, 'Tips/show_tips.html',
                          {'msg': 'maximum number of characters exceeded for title/category'})
        except ValidationError:
            return render(request, 'Tips/show_tips.html',
                          {'msg': 'maximum number of characters exceeded for title/category'})
    else:
        return redirect('show_all_tips')    


@login_required(login_url='/product/user/login')
def delete_tip(request, pk):
    # delete the tip from database

    if request.method == 'POST':
        tip = HealthTip.objects.get(pk=pk)
        tip.delete() 

        tips = HealthTip.objects.all()
        return render(request, 'Tips/show_tips.html',
                      {'msg': 'Health tip deleted successfully!.',
                       'tips': tips})
    else:
        return redirect('show_all_tips')


# ---------------User section------------------#
"""
    This section contain all view functions for the user database
"""


def login(request):
    # login the user and authenticate the username and password

    if request.method == 'POST':

        user = auth.authenticate(request, username=request.POST['username'],
                                 password=request.POST['password'])
        if user is None:
            return render(request, 'user/login.html', {'msg': 'username or password incorrect!'})
        else:
            auth.login(request, user)  
            products = retrieve_products()  
            return render(request, 'products/index.html',
                          {'products': products}) 
    else:
        return render(request, 'user/login.html')


@login_required(login_url='/product/user/login')
def logout(request):
    # log out the user

    if request.method == 'POST':
        auth.logout(request)
        return render(request, 'user/login.html')
    else:
        return redirect('view_admin')
    

@login_required(login_url='/product/user/login')
def change_username(request):
    # change the username

    if request.method == 'POST':
        username = request.user.username
        
        try:
            if str(username).lower() == str(request.POST['username']).lower():
                user = User.objects.get(username=username)
                user.username = request.POST['new_username'] 
                user.save()
                products = retrieve_products()
                return render(request, 'products/index.html',
                                {'products': products,
                                'msg': 'Username successfully changed!.'})   
            else:
                return render(request, 'user/username.html',
                            {'msg': 'Wrong username.'}) 
        except ValidationError:
            return render(request, 'user/username.html',
                          {'msg': 'maximum number of characters exceeded for username'})
    else:
        return render(request, 'user/username.html')    


@login_required(login_url='/product/user/login')
def change_password(request):
    # change password to a new password

    if request.method == 'POST':
        username = request.user.username
        old_password = request.POST['old_password']
        if request.POST['new_password'] == request.POST['confirm_password']:
            user = auth.authenticate(request, username=username, 
                                        password=old_password)
            if user is None:
                return render(request, 'user/password.html',
                        {"msg": "password not correct."}) 
            else:
                new_password = request.POST['new_password']
                user.set_password(new_password)
                user.save()
                # re-authenticate user
                user = auth.authenticate(request, username=username, 
                                         password=new_password)
                if user is None:
                    return render(request, 'user/password.html',
                            {"msg": "password change failed."}) 
                else:
                    products = retrieve_products()
                    return render(request, 'products/index.html', 
                                {'msg': 'Password successfully changed!.',
                                'products': products}) 
        else:
            return render(request, 'user/password.html',
                            {"msg": "new password does not match."})    
    else:
        return render(request, 'user/password.html')       
