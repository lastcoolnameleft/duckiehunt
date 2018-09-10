def handle_uploaded_file(f):
    print('handle_uploaded_file')
    print(f)
    with open('/tmp/' + str(f), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
