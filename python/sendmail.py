import os, base64, sys, getopt

from datetime import datetime
from sendgrid import SendGridAPIClient, Attachment
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from utils.folder_actions import list_files_in_folder

from python_http_client.exceptions import HTTPError

'''Función para enviar email, este código es llamado por la Action de GitHub'''
def main():
    # Obtiene los argumentos de la línea de comandos, excluyendo el nombre del script
    argv = sys.argv[1:]

    try:
        # Analiza los argumentos de la línea de comandos
        opts, args = getopt.getopt(argv,'t:f:c:s', ['to=','from=','content=','subject='])
    except getopt.GetoptError:
        # Muestra el uso correcto del script si hay un error en los argumentos
        print('sendmail.py -t <to-file> -f <from> -c <content-html> -s <subject>')
        sys.exit(2)
    
    # Asigna los argumentos a variables según la opción
    for opt, arg in opts:
        if opt == '-h':
            print('sendmail.py -t <to-file> -f <from> -c <content-html> -s <subject>')
            sys.exit()
        elif opt in ('-t', '--to'):
            to_file = arg
        elif opt in ('-f', '--from'):
            from_addy = arg
        elif opt in ('-c', '--content'):
            cont_file = arg
        elif opt in ('-s', '--subject'):
            subj = arg

    # Lee el archivo que contiene las direcciones de correo destinatarias
    with open(to_file, 'r+') as text_file:
        rawlist = text_file.read().split('\n')
        maillist = [i for i in rawlist if i]
        print(maillist)

    # Lee el contenido HTML del correo electrónico
    with open(cont_file, 'r+') as cfile:
        html_content = cfile.read()

    # Obtiene la lista de archivos de imagen en la carpeta especificada
    images_list = list_files_in_folder('./report/images')

    # Reemplaza las rutas de las imágenes en el contenido HTML con referencias CID
    for image in images_list:
        html_content = html_content.replace(f'images/{image}', f'cid:{image}')
    
    # Crea el objeto de mensaje de correo electrónico
    message = Mail(
        from_email=from_addy,
        to_emails=maillist,
        subject=subj,
        html_content=html_content)
    
    # Adjunta cada imagen al mensaje como contenido en línea (CID)
    for image in images_list:
        with open(f'./report/images/{image}', 'rb') as f:
            data = f.read()
        attachment_file = Attachment(
            disposition='inline',
            file_name=image,
            file_type='image/png',
            file_content=base64.b64encode(data).decode(),
            content_id=image,
        )
        message.add_attachment(attachment_file)

    # Lee el archivo HTML del informe y lo adjunta al mensaje como archivo adjunto
    with open(f'./report/index.html', 'rb') as f:
        data2 = f.read()
        f.close()
    encoded_file = base64.b64encode(data2).decode()
    today = datetime.today()
    filename = "DSOMetrics" + today.strftime("%Y-%m-%d") + ".html"
    html_file = Attachment(
        FileContent(encoded_file),
        FileName(filename),
        FileType('text/html'),
        Disposition('attachment')
    )
    message.add_attachment(html_file)
    
    try:
        # Envía el mensaje usando la API de SendGrid
        sg = SendGridAPIClient(os.environ.get('SENDGRID_SANDBOX_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except HTTPError as e:
        # Maneja errores HTTP específicos de la API de SendGrid
        print(e.to_dict)
        exit(1)
    except Exception as e:
        # Maneja otros errores generales
        print(e.message)
        exit(1)

# Llama a la función main si el script se ejecuta directamente
if __name__ == '__main__':
    main()
