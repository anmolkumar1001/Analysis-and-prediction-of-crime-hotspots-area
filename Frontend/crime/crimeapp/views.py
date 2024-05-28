from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import RandomOverSampler
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
import folium

# Preprocess data function
def preprocess_data():
    global df, x_train, x_test, y_train, y_test
    
    df = pd.read_excel('crimeapp/20230320020226crime_data_extended_entries.xlsx')
    df.drop(["date", "time_of_day"], axis=1, inplace=True)
    
    le = LabelEncoder()
    cols = ['crime_type', 'location', 'victim_gender', 'perpetrator_gender', 'weapon', 'injury', 'weather', 'previous_activity']
    
    for i in cols:
        df[i] = le.fit_transform(df[i])
    
    x = df.drop(['crime_type'], axis=1)
    y = df['crime_type']
    
    Oversample = RandomOverSampler(random_state=72)
    x_sm, y_sm = Oversample.fit_resample(x[:100], y[:100])
    
    x_train, x_test, y_train, y_test = train_test_split(x_sm, y_sm, test_size=0.3, random_state=72)

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration Successful.')
            return redirect('login')
        else:
            messages.error(request, 'Unsuccessful registration.')
    else:
        form = NewUserForm()
    return render(request, 'register.html', {'register_form': form})

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('userhome')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'login_form': form})

def userhome(request):
    return render(request, 'userhome.html')

def view(request):
    global df
    df = pd.read_excel('crimeapp/20230320020226crime_data_extended_entries.xlsx')
    col = df.head(100).to_html()
    return render(request, "view.html", {'table': col})

def moduless(request):
    preprocess_data()
    
    if request.method == "POST":
        model = request.POST['algo']
        
        if model == "1":
            re = RandomForestClassifier(random_state=72)
            re.fit(x_train, y_train)
            re_pred = re.predict(x_test)
            ac = accuracy_score(y_test, re_pred)
            msg = f'Accuracy of RandomForest: {ac}'
            return render(request, 'moduless.html', {'msg': msg})
        
        elif model == "2":
            de = DecisionTreeClassifier()
            de.fit(x_train, y_train)
            de_pred = de.predict(x_test)
            ac1 = accuracy_score(y_test, de_pred)
            msg = f'Accuracy of Decision tree: {ac1}'
            return render(request, 'moduless.html', {'msg': msg})
        
        elif model == "3":
            gd = GradientBoostingClassifier()
            gd.fit(x_train, y_train)
            gd_pred = gd.predict(x_test)
            bc = accuracy_score(y_test, gd_pred)
            msg = f'Accuracy of GradientBoostingClassifier: {bc}'
            return render(request, 'moduless.html', {'msg': msg})
    
    return render(request, 'moduless.html')

def prediction(request):
    preprocess_data()
    
    if request.method == 'POST':
        a = float(request.POST['f1'])
        b = float(request.POST['f2'])
        c = float(request.POST['f3'])
        d = float(request.POST['f4'])
        e = float(request.POST['f5'])
        f = float(request.POST['f6'])
        g = float(request.POST['f7'])
        h = float(request.POST['f8'])
        i = float(request.POST['f9'])
        j = float(request.POST['f10'])
        k = float(request.POST['f11'])
        l = float(request.POST['f12'])
        
        data = [[a, b, c, d, e, f, g, h, i, j, k, l]]
        
        de = DecisionTreeClassifier()
        de.fit(x_train, y_train)
        pred = de.predict(data)
        
        crime_types = ['Robbery', 'Embezzlement', 'Burglary', 'Vandalism', 'Theft', 'Assault', 'Forgery', 'Drug Offense']
        
        msg = crime_types[pred[0]] if pred[0] < len(crime_types) else 'Fraud'
        
        lat = b
        lag = c
        
        m = folium.Map(location=[19, -12], zoom_start=2)
        folium.Marker([lat, lag], tooltip='Click for more', popup=msg).add_to(m)
        m = m._repr_html_()
        
        return render(request, 'result.html', {'msg': msg, 'm': m})
    
    return render(request, 'prediction.html')

       