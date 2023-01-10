import email

def move_mail_to_another_folder(con):
    con.select(mailbox ='Inbox', readonly=False)
    (retcode, messagess) = con.uid('search', None, "ALL")
    if retcode == 'OK':
        for num in messagess[0].split():
            typ, data = con.uid('fetch', num, '(RFC822)')
            msg = email.message_from_bytes((data[0][1]))
            # MOVE MESSAGE TO ProcessedEmails FOLDER
            result = con.uid('COPY', num, 'Used')
            if result[0] == 'OK':
                mov, data = con.uid('STORE', num, '+FLAGS', '(\Deleted)')
                con.expunge()
    con.close()