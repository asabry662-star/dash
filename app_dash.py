import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np
# from pyairtable import Table # يمكن إلغاء التعليق على هذا السطر عند ربط Airtable فعلياً

# ====================================================================
# 1. الإعدادات والثوابت والتصميم (Colors & CSS)
# ====================================================================

# الألوان للهوية البصرية (Dark Blue, Gold Accent)
COLORS = {
    'background': '#F8F9FA',      # خلفية التطبيق الفاتحة
    'sidebar_bg': '#FFFFFF',      # خلفية القائمة الجانبية (بيضاء)
    'header_bg': '#003366',       # خلفية الشريط العلوي الداكنة
    'primary_dark': '#003366',    # اللون الأساسي الداكن
    'accent_gold': '#FFD700',     # لون التمييز الذهبي (للحدود أو الخطوط)
    'text_light': '#FFFFFF',      # لون النص الفاتح
    'text_dark': '#333333',       # لون النص الداكن
    'success': '#28A745',         # أخضر
    'danger': '#DC3545',          # أحمر
}

# نمط CSS خارجي لدعم اللغة العربية (RTL) واستخدام خط 'Tajawal'
EXTERNAL_STYLESHEETS = [
    # Dash CSS الأساسي لتوفير نظام الأعمدة (columns)
    'https://codepen.io/chriddyp/pen/bWLwgP.css', 
    {
        # إضافة خط عربي احترافي
        'href': 'https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap',
        'rel': 'stylesheet'
    }
]

# ====================================================================
# 2. تحميل ومعالجة البيانات (باستخدام بيانات وهمية)
# ====================================================================

def load_and_process_data():
    """محاكاة تحميل ومعالجة البيانات من Airtable."""
    
    # 1. محاكاة بيانات Airtable
    np.random.seed(42)
    data = {
        'Contract_ID': [f'C{i:03d}' for i in range(1, 11)],
        'Report_Date': pd.to_datetime(pd.date_range('2024-01-01', periods=10, freq='M')),
        'Category': ['انارة'] * 5 + ['طرق'] * 5,
        'Actual_Completion_Rate': np.random.rand(10) * 0.7 + 0.3,
        'Target_Completion_Rate': np.random.rand(10) * 0.2 + 0.7,
        'Contractor_Overall_Score': np.random.uniform(75, 95, 10),
        'Actual_Financial_Value': np.random.randint(10, 50, 10) * 1000000,
        'Target_Financial_Value': np.random.randint(10, 40, 10) * 1000000,
        'HSE_Score': np.random.uniform(80, 100, 10),
        'Quality_Score': np.random.uniform(70, 90, 10),
    }
    df = pd.DataFrame(data)

    # 2. حساب الأعمدة المطلوبة
    df['Actual_Deviation_Rate'] = df['Actual_Completion_Rate'] - df['Target_Completion_Rate']
    df['Project_Deviation_Status'] = df['Actual_Deviation_Rate'].apply(
        lambda x: 'متقدم' if x >= 0.05 else ('متأخر' if x <= -0.05 else 'مطابق')
    )
    
    # 3. استخراج أحدث التقارير لكل عقد
    df_latest = df.loc[df.groupby('Contract_ID')['Report_Date'].idxmax()]
    
    # (هنا يجب إضافة منطق pyairtable الفعلي عند ربط البيانات)
    return df, df_latest

# تحميل البيانات عند بدء التطبيق
df_all, df_latest = load_and_process_data()

# ====================================================================
# 3. تعريف مكونات التصميم الاحترافية (KPI Card)
# ====================================================================

def kpi_card(title, value, delta=None, color=COLORS['primary_dark']):
    """مكون بطاقة KPI بتصميم احترافي (Card-based)."""
    
    delta_style = {}
    if delta is not None:
        delta_color = COLORS['success'] if delta >= 0 else COLORS['danger']
        delta_text = f"({'+' if delta >= 0 else ''}{delta:.1f}%)"
        delta_style = {'color': delta_color, 'fontSize': 14, 'fontWeight': 'bold', 'marginRight': '10px'}

    return html.Div([
        html.H6(title, style={'color': COLORS['text_dark'], 'marginBottom': '5px', 'fontWeight': 'normal', 'textAlign': 'right'}),
        html.P(value, style={'fontSize': '2.5em', 'fontWeight': '900', 'color': color, 'textAlign': 'right', 'margin': '0'}),
        html.Span(delta_text if delta is not None else '', style=delta_style),
    ], style={
        'backgroundColor': COLORS['sidebar_bg'],
        'borderRadius': '12px',
        'padding': '20px',
        # ظل خفيف يعطي إحساس العمق
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
        # الحد الجانبي الملون
        'borderRight': f'5px solid {color}',
        'marginBottom': '20px',
        'height': '100%',
        'direction': 'rtl'
    })

# ====================================================================
# 4. بناء هيكل التطبيق (The Layout)
# ====================================================================

# تهيئة تطبيق Dash
app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)

app.layout = html.Div(style={
    'backgroundColor': COLORS['background'],
    'fontFamily': 'Tajawal, sans-serif',
    'direction': 'rtl',
    'padding': '0'
}, children=[
    
    # الشريط العلوي (Header Bar) - تصميم داكن
    html.Div([
        html.H1("نظام متابعة أداء عقود التشغيل والصيانة", style={
            'color': COLORS['text_light'], 
            'margin': '0', 
            'fontSize': '1.8em',
            'fontWeight': '900'
        }),
    ], style={
        'backgroundColor': COLORS['header_bg'],
        'padding': '15px 30px',
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'direction': 'rtl'
    }),
    
    # المحتوى الرئيسي (Sidebar + Main Content)
    html.Div([
        # 4.1. القائمة الجانبية (Filters) - في عمود واحد
        html.Div([
            html.H3("تصفية البيانات", style={
                'color': COLORS['primary_dark'], 
                'paddingBottom': '10px', 
                'borderBottom': '1px solid #eee',
                'marginBottom': '20px'
            }),
            
            html.Label("التصنيف:", style={'display': 'block', 'marginTop': '10px', 'color': COLORS['text_dark']}),
            dcc.Dropdown(
                id='category-filter',
                options=[{'label': i, 'value': i} for i in df_all['Category'].unique()],
                value='انارة',
                clearable=False,
                style={'direction': 'rtl', 'textAlign': 'right', 'fontFamily': 'Tajawal'}
            ),
            
            html.Label("رقم العقد:", style={'display': 'block', 'marginTop': '20px', 'color': COLORS['text_dark']}),
            dcc.Dropdown(
                id='contract-filter',
                options=[{'label': i, 'value': i} for i in df_latest['Contract_ID'].unique()],
                value=[df_latest['Contract_ID'].unique()[0]],
                multi=True,
                style={'direction': 'rtl', 'textAlign': 'right', 'fontFamily': 'Tajawal'}
            ),
            
            html.Div(style={'marginTop': '30px'}, children=[
                html.P("لوحة تحكم احترافية بتصميم Plotly Dash", style={'color': COLORS['primary_dark'], 'fontWeight': 'bold'}),
                html.P("تم استخدام مكونات Dash الأساسية (dcc و html) لضمان التوافق التام.", style={'fontSize': '12px', 'color': '#666'})
            ])
            
        ], style={
            'width': '25%', 
            'padding': '20px', 
            'backgroundColor': COLORS['sidebar_bg'], 
            'boxShadow': '2px 0 5px rgba(0, 0, 0, 0.05)',
            'float': 'right',
            'height': 'calc(100vh - 75px)',
            'overflowY': 'auto'
        }),
        
        # 4.2. لوحة المؤشرات الرئيسية (KPIs & Charts)
        html.Div([
            html.H2("ملخص تنفيذي", style={
                'color': COLORS['primary_dark'], 
                'paddingBottom': '10px', 
                'borderBottom': f'3px solid {COLORS["accent_gold"]}',
                'marginBottom': '30px'
            }),
            
            # KPIs Row 1: (تتم إضافة المحتوى عبر Callback)
            html.Div(id='kpis-row-1', className='row', style={'padding': '0 15px'}),
            
            # Chart Row: مخطط الإنجاز
            html.Div([
                html.H3("تتبع أداء الإنجاز الزمني", style={'color': COLORS['primary_dark'], 'marginTop': '30px', 'textAlign': 'right'}),
                dcc.Graph(id='completion-chart', config={'displayModeBar': False}, 
                          style={'borderRadius': '12px', 'overflow': 'hidden', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
            ], className='row', style={'padding': '0 15px', 'marginTop': '30px'}),
            
        ], style={
            'width': '75%', 
            'float': 'left',
            'padding': '30px',
            'direction': 'rtl'
        }),
    ], className='container-fluid', style={'padding': '0'})
])

# ====================================================================
# 5. التفاعلية والـ Callbacks
# ====================================================================

@app.callback(
    [Output('kpis-row-1', 'children'),
     Output('completion-chart', 'figure')],
    [Input('category-filter', 'value'),
     Input('contract-filter', 'value')]
)
def update_dashboard(selected_category, selected_contracts):
    
    # 1. فلترة البيانات بناءً على الاختيارات
    filtered_df = df_latest[df_latest['Category'] == selected_category].copy()
    
    if selected_contracts and 'All' not in selected_contracts:
        filtered_df = filtered_df[filtered_df['Contract_ID'].isin(selected_contracts)]

    if filtered_df.empty:
        return [html.Div("لا توجد بيانات مطابقة لمعايير الفلترة المحددة.", style={'color': COLORS['danger'], 'padding': '20px'})], px.scatter()


    # 2. حساب المؤشرات الرئيسية (KPIs)
    
    avg_actual_completion = filtered_df['Actual_Completion_Rate'].mean() * 100
    avg_target_completion = filtered_df['Target_Completion_Rate'].mean() * 100
    completion_delta = avg_actual_completion - avg_target_completion
    
    avg_overall_score = filtered_df['Contractor_Overall_Score'].mean()
    
    total_projects = filtered_df.shape[0]
    late_count = filtered_df[filtered_df['Project_Deviation_Status'] == 'متأخر'].shape[0]
    
    total_actual_value_m = filtered_df['Actual_Financial_Value'].sum() / 1000000
    
    
    # 3. بناء صف KPI Cards باستخدام نظام الأعمدة Dash (className='three columns')
    kpis_row = [
        # KPI 1: متوسط الإنجاز الفعلي
        html.Div(kpi_card(
            "متوسط الإنجاز الفعلي", 
            f"{avg_actual_completion:.1f}%", 
            delta=completion_delta, 
            color=COLORS['success']
        ), className='three columns', style={'direction': 'rtl'}),
        
        # KPI 2: متوسط التقييم العام
        html.Div(kpi_card(
            "متوسط التقييم العام", 
            f"{avg_overall_score:.2f}",
            color=COLORS['primary_dark']
        ), className='three columns', style={'direction': 'rtl'}),
        
        # KPI 3: المشاريع المتأخرة
        html.Div(kpi_card(
            "المشاريع المتأخرة", 
            f"{late_count} / {total_projects}", 
            color=COLORS['danger']
        ), className='three columns', style={'direction': 'rtl'}),
        
        # KPI 4: القيمة الفعلية المنفذة
        html.Div(kpi_card(
            "إجمالي القيمة المنفذة", 
            f"{total_actual_value_m:,.1f}M", 
            color=COLORS['primary_dark']
        ), className='three columns', style={'direction': 'rtl'}),
    ]

    # 4. بناء مخطط الإنجاز الشهري (Line Chart)
    
    df_chart = df_all[df_all['Category'] == selected_category].copy()
    
    if selected_contracts and 'All' not in selected_contracts:
        df_chart = df_chart[df_chart['Contract_ID'].isin(selected_contracts)]
        
    monthly_data = df_chart.groupby(df_chart['Report_Date'].dt.to_period('M'))[[
        'Actual_Completion_Rate', 'Target_Completion_Rate'
    ]].mean().reset_index()
    
    monthly_data['Report_Date'] = monthly_data['Report_Date'].dt.to_timestamp()
    monthly_data['Actual_Completion_Rate'] = monthly_data['Actual_Completion_Rate'] * 100
    monthly_data['Target_Completion_Rate'] = monthly_data['Target_Completion_Rate'] * 100
    
    fig_completion = px.line(
        monthly_data, x='Report_Date', y=['Actual_Completion_Rate', 'Target_Completion_Rate'], 
        labels={
            'value': 'النسبة المئوية', 
            'Report_Date': 'تاريخ التقرير', 
            'variable': 'مؤشر الإنجاز'
        },
        color_discrete_map={
            'Actual_Completion_Rate': COLORS['success'], 
            'Target_Completion_Rate': COLORS['primary_dark']
        }
    )
    
    fig_completion.update_layout(
        plot_bgcolor=COLORS['sidebar_bg'],
        paper_bgcolor=COLORS['sidebar_bg'],
        margin=dict(l=40, r=40, t=10, b=40),
        legend_title_text='المؤشر',
        font=dict(family='Tajawal', size=12, color=COLORS['text_dark']),
        xaxis_title=None, 
        yaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="right", x=1)
    )
    fig_completion.for_each_trace(lambda t: t.update(name = "الفعلي" if t.name == 'Actual_Completion_Rate' else "المخطط"))

    return kpis_row, fig_completion


if __name__ == '__main__':
    # تشغيل التطبيق في وضع التطوير (Debug Mode)
    app.run_server(debug=True)
