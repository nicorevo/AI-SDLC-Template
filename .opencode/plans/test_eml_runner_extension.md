# Piano: Estensione `test_eml_runner.py`

Il runner copre solo il flusso base EML → `extract_info_mail` (6/20 campi). Manca la validazione del Kafka payload, dei headers, del self-test completo e dei rami secondari. Ecco le modifiche precise per portarlo a copertura funzionale ≥80%.

## 1. Fix datetime naive crash
- **File**: `test_eml_runner.py`
- **Line**: 23, 200-202
- **Problem**: `datetime(2026, 7, 15, 10, 0, 0)` crea datetime naive. `mail_reader.py:1044,1124` chiama `.astimezone(pytz.timezone('Europe/Rome'))` che lancia `AttributeError` su naive datetimes.
- **Solution**:
```python
# +1 riga dopo import datetime
import pytz

# Sostituire righe 200-202 in build_mock_message
dt = datetime(2026, 7, 15, 10, 0, 0, tzinfo=pytz.UTC)
msg.datetime_received = dt
msg.datetime_sent = dt
```

## 2. Espandere verifica campi `extract_info_mail` da 6 a 20+
- **File**: `test_eml_runner.py`
- **Line**: 532-533
- **Problem**: Verifica solo `['tep_subject', 'tep_from', 'tep_to', 'tep_body', 'tep_attachment', 'tep_messageid']`. `mail_reader.py:1029-1130` produce 20 campi.
- **Solution**: Sostituire righe 532-541 con validazione completa:
```python
all_expected_fields = [
    'tep_flusso', 'tep_messageid', 'tep_exchangemailuri', 'tep_sentdatelocal',
    'tep_from', 'tep_fromname', 'tep_replyto', 'tep_replytoname',
    'tep_to', 'tep_toname', 'tep_cc', 'tep_ccname',
    'tep_bcc', 'tep_bccname', 'tep_subject', 'tep_bodytype',
    'tep_body', 'tep_attachment', 'tep_sourcefolder', 'tep_receiveddateonserver'
]
print('    --- All {} Expected Fields ---'.format(len(all_expected_fields)))
for req in all_expected_fields:
    found = req in field_names
    val = next((item['value'] for item in msg_data if item['name'] == req), '')
    val_preview = str(val)[:150] if val else '(none)'
    print('      {} {} -> {}'.format('OK' if found else 'MISS', req, val_preview))
    if not found:
        errors.append('Missing required field: {}'.format(req))
```

## 3. Mock & validare `produce_message` (Kafka payload + headers)
- **File**: `test_eml_runner.py`
- **Line**: Inserire dopo riga 560 (fine blocco `extract_info_mail`)
- **Problem**: Runner si ferma a `extract_info_mail`. Il flusso reale (`mail_reader.py:384`) invoca `produce_message()` che costruisce dict payload + headers e chiama `MessageProducer.send_msg()`.
- **Solution**:
```python
    # ---- produce_message (Kafka) ----
    print('\n  --- Running produce_message (Kafka) ---')
    from producer_message import produce_message
    
    mock_producer = MagicMock()
    mock_producer.send = MagicMock(return_value=MagicMock())
    mock_producer.flush = MagicMock()
    
    kafka_patcher = patch('producer_message.MessageProducer', return_value=mock_producer)
    kafka_patcher.start()
    
    kafka_ok = True
    try:
        produce_message(
            correlation_id='test-123', task_id='80308', nr_polizza='OX12345678',
            nr_sinistro='', key_polizza='11111111-1111-1111-1111-111111111111',
            user='test-account', file_path='temp/test.eml',
            list_attachments_path=list_attachments,
            list_attachments_path_not_inline=list_not_inline,
            list_attachments_path_inline=list_inline,
            message_key='TEST-key', msg_data=msg_data,
            entityType='EMAIL-INGESTION', flusso_ccontact=123
        )
        print('    Return:    PASSED')
    except Exception as e:
        errors.append('produce_message failed: {}'.format(str(e)))
        kafka_ok = False
        print('    ERROR:     {}'.format(str(e)))
    
    # Validare struttura payload
    call_args = mock_producer.send.call_args
    payload = call_args[0][0] if call_args[0] else None
    
    expected_keys = ['taskId','nr_polizza','nr_sinistro','key_polizza','account',
                     'path_eml','path_attachments','path_attachments_not_inline',
                     'path_attachments_inline','msg_data','flusso_cc','references','in_reply_to']
    if payload:
        missing = [k for k in expected_keys if k not in payload]
        print('    Payload:   {} present, missing: {}'.format(len(expected_keys)-len(missing), missing))
        if missing: errors.append('Kafka payload missing: {}'.format(missing))
        # Types validation
        for k in ['path_attachments','path_attachments_not_inline','path_attachments_inline','msg_data']:
            if not isinstance(payload.get(k), list):
                errors.append('Kafka payload {} must be list'.format(k))
    else:
        errors.append('Kafka payload was None')
        kafka_ok = False
    
    # Validare headers
    headers = call_args[0][2] if len(call_args[0]) > 2 else None
    if headers:
        hdr_keys = [h[0] for h in headers]
        expected_hdrs = ['status','entityType','entityId','correlationId']
        miss_h = [k for k in expected_hdrs if k not in hdr_keys]
        print('    Headers:   {} present, missing: {}'.format(len(expected_hdrs)-len(miss_h), miss_h))
        if miss_h: errors.append('Missing Kafka headers: {}'.format(miss_h))
    
    kafka_patcher.stop()
    summary['kafka_ok'] = kafka_ok
```

## 4. Mock `produce_message_validazione` & test branch validazione
- **File**: `test_eml_runner.py`
- **Line**: Aggiungere nuovo CLI mode `--test-validazione` dopo riga 733
- **Problem**: Branch "Richiesta di Validazione" (`mail_reader.py:242-317`) non testato.
- **Solution**:
```python
    if args[0] == '--test-validazione':
        print('Running validazione flow self-test...')
        from email.mime.multipart import MIMEMultipart, MIMEText
        m = MIMEMultipart()
        m['Subject'] = 'Richiesta di Validazione'
        m['From'] = 'test@example.com'
        m.attach(MIMEText('Numero polizza: OX12345678', 'plain'))
        raw = m.as_bytes()
        
        # Patch extraction functions
        with patch('mail_reader.extract_data', return_value={'Numero polizza': 'OX12345678'}), \
             patch('mail_reader.get_numero_polizza', return_value={'is_polizza': True, 'key_p': 'test-key'}), \
             patch('mail_reader.build_entity_id', return_value='entity-1'):
            
            parsed = parse_eml_bytes(raw)
            mock = build_mock_message(parsed, raw)
            
            # Mock produce_message_validazione
            mock_val_producer = MagicMock()
            mock_val_producer.send = MagicMock(return_value=MagicMock())
            
            with patch('producer_message.MessageProducer', return_value=mock_val_producer):
                from producer_message import produce_message_validazione
                produce_message_validazione(
                    correlation_id='val-123',
                    payload={'Numero polizza': 'OX12345678'},
                    file_path='temp/val.eml',
                    message_key='VAL-key',
                    entityType='Richiesta di Validazione',
                    flusso_ccontact=456
                )
                
                call_a = mock_val_producer.send.call_args
                payload = call_a[0][0]
                headers = call_a[0][2]
                
                print('    Payload keys:      {}'.format(list(payload.keys())))
                print('    Headers present:    {}'.format([h[0] for h in headers]))
                # Validare che headers contengano tipoEntita e tipoEvento
                hdr_names = [h[0] for h in headers]
                if 'tipoEntita' in hdr_names and 'tipoEvento' in hdr_names:
                    print('    Validazione headers: OK')
                else:
                    print('    Validazione headers: MISSING')
                    sys.exit(1)
        print('\n  Self-test validazione: PASS')
        return
```

## 5. Migliorare `--test` self-test con EML completo
- **File**: `test_eml_runner.py`
- **Line**: 693-733
- **Problem**: Self-test minimo (1 subject, 1 att, no CC/BCC/Reply-To/nomi).
- **Solution**: Sostituire blocco `--test` con EML multipart completo:
  - Headers: `From` con nome, 3 `To`, 2 `Cc`, 1 `Bcc`, 1 `Reply-To`
  - Body: HTML + Plain text
  - Allegati: 2 normali (PDF, CSV), 1 inline (PNG con Content-ID)
  - Nome RFC 2047 non-ASCII
  - Write a temp `.eml` e lanciare `run_pipeline()` su di esso
  - Verificare `len(mock.to_recipients) >= 2`, `len(mock.cc.recipients) >= 2`, ecc.
  - Stampare summary pipeline: `Fields found`, `All fields`, `Attachments extracted`, `Unique paths`, `S3 calls`

## 6. Validare `tep_references` & `tep_in_reply_to` nel flusso completo
- **File**: `test_eml_runner.py`
- **Line**: ~Line 37 (patch), 404-520 (pipeline)
- **Problem**: Questi campi sono aggiunti DOPO `extract_info_mail` in `mail_reader.py:357-367`. Non sono nel diretto output della funzione.
- **Solution**: Durante il mock di `produce_message`, verificare che i payload `references` e `in_reply_to` corrispondano ai valori estratti da `msg.references` e `msg.in_reply_to` nel mock message. Aggiungere al self-test EML i headers `References: <thread-id@example.com>` e `In-Reply-To: <parent-id@example.com>`. Verificare che `mock.references` e `mock.in_reply_to` siano valorizzati e transitino nel payload Kafka.

## 7. Aggiornare output summary per Kafka
- **File**: `test_eml_runner.py`
- **Line**: 589-593 (`print_result`), 630 (`scan_directory`)
- **Problem**: Riepilogo non riflette stato produzione Kafka.
- **Solution**: 
```python
# In print_result, dopo "Unique P:"
print('    Kafka:         {}'.format('produced OK' if summary.get('kafka_ok') else 'SKIPPED'))

# In scan_directory table header
print('  {:4s}  {:40s}  {:5s}  {}'.format('PASS', 'FILE', 'ATT', 'KAFKA'))
# Nello stampaggio riga: includere summary.get('kafka_ok', False)
```

## Riepilogo esecuzione
| # | Task | Difficoltà | Tempo stimato |
|---|------|------------|---------------|
| 1 | Fix datetime naive | Facile | 5m |
| 2 | Espandere campi a 20+ | Facile | 10m |
| 3 | Mock & validare Kafka payload/headers | Media | 20m |
| 4 | Mock validazione branch | Media | 15m |
| 5 | Self-test EML completo | Media | 20m |
| 6 | Validare references/in_reply_to | Facile | 10m |
| 7 | Aggiornare output summary | Facile | 5m |
|   | **Totale** | | **~75m** |

**Nota per l'agent**: Eseguire Task 1 prima di tutti gli altri (corregge un crash bloccante). Testare ogni task con `python test_eml_runner.py --test` prima di passare al successivo. Mantenere compatibilità Python 3.8 (no f-string, no walrus operator, no `match/case`).
