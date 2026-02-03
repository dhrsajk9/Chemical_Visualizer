import pandas as pd
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from sklearn.ensemble import IsolationForest 

from .models import EquipmentData
from .serializers import EquipmentDataSerializer

# 1. Custom Auth View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk})

# 2. File Upload & History View
class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated] # Basic Auth Requirement

    def get(self, request):
        # Return last 5 uploads
        files = EquipmentData.objects.order_by('-uploaded_at')[:5]
        serializer = EquipmentDataSerializer(files, many=True)
        return Response(serializer.data)

    def post(self, request):
        file_serializer = EquipmentDataSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            
            # Enforce "Keep only last 5" history requirement 
            all_files = EquipmentData.objects.order_by('-uploaded_at')
            if all_files.count() > 5:
                files_to_delete = all_files[5:]
                for f in files_to_delete:
                    # Optional: Delete actual file from disk to save space
                    if os.path.exists(f.file.path):
                        os.remove(f.file.path)
                    f.delete()
                    
            return Response(file_serializer.data, status=201)
        return Response(file_serializer.errors, status=400)

# 3. Analytics View 
class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            data_obj = EquipmentData.objects.get(pk=pk)
            file_path = data_obj.file.path
            
            # 1. Load Data
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            
            # 2. AI Implementation: Anomaly Detection
            # We select numeric features for the model
            features = ['Flowrate', 'Pressure', 'Temperature']
            
            # Ensure columns exist and fill NaNs to prevent crashes
            if set(features).issubset(df.columns):
                # Initialize Isolation Forest (Contamination = 5% of data is likely noise)
                model = IsolationForest(contamination=0.05, random_state=42)
                
                # Fit and Predict (-1 is anomaly, 1 is normal)
                df['anomaly_score'] = model.fit_predict(df[features])
                
                # Convert to boolean for easier frontend handling
                df['is_anomaly'] = df['anomaly_score'].apply(lambda x: True if x == -1 else False)
            else:
                df['is_anomaly'] = False # Fallback if columns missing

            # 3. Standard Stats (Existing code)
            total_count = len(df)
            numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
            averages = {col: df[col].mean() for col in numeric_cols if col in df.columns}
            type_distribution = df['Type'].value_counts().to_dict() if 'Type' in df.columns else {}

            # 4. Return Full Data with Anomaly Flags
            # We return the whole dataset (or first 100 rows) so we can plot it
            return Response({
                "filename": data_obj.filename(),
                "total_count": total_count,
                "averages": averages,
                "type_distribution": type_distribution,
                "dataset": df.head(100).to_dict(orient='records') # Sent 100 rows for scatter plot
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# 4. PDF Generation View 
class PDFReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            data_obj = EquipmentData.objects.get(pk=pk)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'

            # Create PDF
            p = canvas.Canvas(response)
            p.drawString(100, 800, f"Equipment Report for: {data_obj.filename()}")
            
            # Fetch Data for report
            df = pd.read_csv(data_obj.file.path)
            y = 750
            p.drawString(100, y, f"Total Equipment Count: {len(df)}")
            y -= 20
            
            if 'Type' in df.columns:
                p.drawString(100, y, "Type Distribution:")
                dist = df['Type'].value_counts().to_dict()
                for k, v in dist.items():
                    y -= 15
                    p.drawString(120, y, f"- {k}: {v}")
            
            p.showPage()
            p.save()
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)