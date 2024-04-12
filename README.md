# SISTEMA BANCARIO

Il progetto implementa le principali funzioni di un sistema bancario, vengono riprodotti servizi elementari come la
creazione di un account, la chiusura di un account, il versamento e prelievo di denaro e lo spostamento di denaro da un account ad un altro.

### TECNOLOGIE IMPLEMENTATE

Il progetto è stato sviluppato utilizzando le seguenti tecnologie: Python (+ django), HTML, CSS

## INSTALLAZIONE

Per eseguire correttamente il progetto è necessario avere installata sulla macchina una versione recente dell'interprete di Python, successivamente seguire le istruzioni:

1. Spostarsi con il terminale nella directory del progetto

2. Creare un virtual environment con il comando: python -m venv .\venv (o in alternativa: py -m venv .\venv)

3. Eseguire il comando: venv\scripts\activate

4. Eseguire il comando: pip install -r requirements.txt

5. Eseguire infine il comando: python manage.py runserver (o in alternativa py manage.py runserver)

<div align=center>
  <img width="350" alt="Senza titolo" src="https://github.com/scio97/SistemaBancario/assets/56976553/bf0e3269-f0c6-4164-babe-48ddf33376d8">
</div>

## STRUTTURA DEL PROGETTO

La struttura del progetto è composta da più file:

* Il file "**urls.py**" di base autogenerato da Django all'avvio del progetto contiene la lista di path nell’oggetto “urlpatterns",
  qui specifichiamo tutti gli uri raggiungibili e le azioni corrispondenti.
  Per l'accesso alle due pagine web facciamo riferimento al file pages che dispone degli appositi metodi per restituire la pagina corrispondente all'URL.
  La gestione delle richieste agli endpoint delle API sono vengono gestiti da views.py

* Il file "**models.py**" contiene i modelli degli oggetti utilizzati dal progetto (Account e Transaction)
  che vengono associati a tabelle autogenerate dal sistema con i comandi per la migrazione

* Il file "**serializer.py**" contiene oggetti utili per la Serializzazione degli oggetti,
  viene utilizzata principalmente dopo aver interrogato il database o per creare gli oggetti con i dati inviati alle API

* Il file “**views.py**” contiene le funzioni per la gestione delle richieste ricevute tramite API,
  ogni funzione è preceduta da un decorator che specifica i metodi http gestiti.

* Il file “**utility.py**” contiene funzioni più volte richiamate dalla views.py

## SCELTE IMPLEMENTATIVE

I prelievi e i depositi vengono memorizzati come transazioni con receiver=null.

Django mette a disposizione dei developer l'endpoint "admin/" per visualizzare graficamente il contenuto del database ai fini di debugging
(credenziali = username: admin ; password: admin).

Per evitare un numero eccessivo di richieste al server è stata implementata una funzione che restituisce nome, cognome, saldo e lista di transazioni effettuate,
accessibile tramite l’endpoint “/api/account/{idAccount}/” utilizzata per la richiesta dei dati dalla pagina “index.html”.

## FRONTEND

Il frontend dell’applicazione è composto da due semplici pagine HTML:

* index.html ( root “/” ): La pagina consente di ricercare attraverso un form le transazioni effettuate dai singoli utenti
  e visualizzarle mediante una apposita tabella in ordine cronologico con la prima riga in grassetto,
  in caso di errori durante la ricerca, la pagina restituisce un messaggio di alert contenente un messaggio di errore appropriato.
  I controlli relativi alla correttezza sintattica della stringa inserita vengono effettuati lato client.

* transfer.html ( path “/transfer” ): La pagina consente di effettuare nuove transazioni specificando i dati necessari attraverso una apposita form e visualizzarne l’esito,
  anche in questo caso viene implementata una logica di controllo dei dati lato client mostrando all’utente eventuali errori sintattici.

Entrambe le pagine HTML utilizzano JavaScript per rendere dinamica la pagina, effettuare i controlli lato client e comunicare con il server tramite XMLHttpRequest.

## DOCUMENTAZIONE ENDPOINT REST

### **/api/account**

  * GET: restituisce la lista di tutti gli account nel sistema.
  * POST: crea un nuovo account con i seguenti campi:

    - name
    - surname

    e ritorna nel body della risposta il nuovo id dell’account creato.
    L’id di un account è una stringa di 20 caratteri rappresentante una sequenza di bytes, generati randomicamente all’occorrenza,
    codificati in esadecimale (ad esempio un accountId potrebbe essere 1087b347f1a59277eb98).

  * DELETE: elimina l'account con id specificato dal parametro URL id

### **/api/account/{accountId}**

  * GET: restituisce il nome e cognome del proprietario nonchè il saldo con un elenco degli identificativi di tutte le transazioni effettuate da accountId,
    in ordine cronologico ascendente. Inoltre, introduce un header di risposta con chiave X-Sistema-Bancario.
    Il valore dell’header esprime il nome e cognome del proprietario in formato nome;cognome.

  * POST: effettua un versamento di denaro con un importo specificato dalla chiave amount nel body della richiesta.
    Se amount è negativo, viene eseguito un prelievo. Nel caso di amount negativo,
    il server genera un errore se il saldo del conto non è sufficiente, informando il client dell’insuccesso.
    In caso di successo, nel body della risposta viene restituito il nuovo saldo del conto ed un identificativo del versamento/prelievo in formato UUID v4.
    
  * PUT: modifica (sovrascrive) name e surname del proprietario del conto. Nel body devono quindi essere presenti le seguenti chiavi:
    
    - name
    - surname
      
  * PATCH: modifica (sovrascrive) name oppure surname del proprietario del conto. Nel body deve quindi essere presente solamente una tra le seguenti chiavi:
    
    - name
    - surname
      
  * HEAD: restituisce nome e cognome del proprietario in un header di risposta con chiave X-Sistema-Bancario.
    Il valore dell’header deve essere in formato nome;cognome. Non deve essere presente alcun body di risposta.

### **/api/transfer**

  * POST: effettua uno spostamento di denaro con amount positivo da un account a un altro. amount è specificato nel body della richiesta.
    Il server genera un errore se il saldo del conto di partenza non è sufficiente, informando il client dell’insuccesso. In caso di successo,
    nel body della risposta vengono restituiti i nuovi saldi degli account coinvolti nella transazione distinti per accountId ed un identificativo della transazione
    in formato UUID v4. Il body della richiesta presenta quindi i seguenti campi:

    - from
    - to
    - amount

### **/api/divert**

  * POST: annulla una transazione con id specificato dalla chiave id nel body della richiesta ovvero crea una nuova transazione con un nuovo UUID v4
    che inverte il trasferimento di denaro tra gli account interessati dalla transazione con identificativo id dell’ammontare che la transazione ha coinvolto,
    ma solamente se il saldo dell’account del precedente beneficiario consente questa operazione. In caso contrario genera un errore.

## DOCUMENTAZIONE FRONTEND WEB

Entrambe le pagine hanno una logica di controllo dell’input prima di inviare una richiesta al backend.
Inoltre, il backend esegue nuovamente il controllo dell’input prima di processare la richiesta.
Se l’input non è corretto, restituisce un errore opportuno che la pagina è in grado di segnalare all’utente.

### **/ _(l’endpoint root del server)_** 

Questa pagina HTML mostra all’utente un prompt con un campo di testo in cui inserire un identificativo di un account e, alla pressione di un bottone,
la pagina si popola con le informazioni riguardanti il proprietario dell’account e lo storico delle transazioni
con associato eventuale destinatario dello spostamento di denaro (non presente se si trattava di un prelievo/versamento) e l’ammontare coinvolto.

### **/transfer**

Questa pagina HTML mostra all’utente un prompt con tre campi di testo in cui inserire account mittente, account destinatario e un ammontare da trasferire, e,
alla pressione di un bottone, viene registrata nel sistema la relativa transazione. La pagina fornisce inoltre un feedback all’utente riguardante l’esito dell’operazione















