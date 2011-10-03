from forms import MyForm
from file_formpreview import FileFormPreview

def upload(request):
    return FileFormPreview(MyForm)(request)
