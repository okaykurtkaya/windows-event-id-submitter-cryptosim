# ########################################
import requests                          #
from requests.auth import HTTPBasicAuth  #
from datetime import datetime, timedelta #
from redminelib import Redmine           #
import redminelib                        #
import sys                               #
import warnings                          #
import logging                           #
# ########################################

# LOGGING
logging.basicConfig(
    filename=f"eventID-submitter-ikea.log",
    filemode='a',
    format='%(asctime)s : %(levelname)s : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    encoding="utf-8")

class EventIDSubmitter:
    def __init__(self):
        # <CrytoSIM URL>/api/service/correlationalertswithlogs
        self.baseURL = "http://<systemName>.cryptosim.local/api/service/correlationalertswithlogs"
        # <RedmineURL>
        self.ticket_url = "https://ticket.<ticketSystemName>.com"
        self.today_date = datetime.now().strftime('%d.%m.%Y')
        # WINDOWS EVENTS
        self.windows_event_ids = {
            "4720": ["A user account was created", "Yeni Kullanıcı Oluşturulması (Event_ID: 4720)", "+Bu olay+, yeni bir kullanıcı hesabı *oluşturulduğunda* gözlemlenmektedir.\n", "adlı kullanıcı hesabının oluşturulduğu tespit edilmiştir.\n", set()],
            "4722": ["A user account was enabled", "Kullanıcı Hesabının Etkinleştirilmesi (Event_ID: 4722)", "+Bu olay+, bir kullanıcı hesabı *etkinleştirildiğinde* gözlemlenmektedir.\n", "adlı kullanıcı hesabının etkinleştirildiği tespit edilmiştir.\n", set()],
            "4723": ["Account Password Change Request for Same User", "Çok Sayıda Parola Sıfırlama İsteği (Event_ID: 4723)", "+Bu olay+, bir kullanıcı parolasını *her değiştirmeye* çalıştığında oluşur.\n+Domain hesapları için+; yeni parola, *parola ilkesini karşılayamazsa* bir hata olayı oluşur.\n+Yerel hesaplar için+; yeni parola parola ilkesini karşılayamazsa veya *eski parola yanlışsa* bir hata olayı oluşur.\n", "adlı kullanıcı hesabının bu duruma sebebiyet verdiği tespit edilmiştir.\n", set()],
            "4724": ["An attempt was made to reset an account's password", "Parola Sıfırlama Denemesi (Event_ID: 4724)", "+Bu olay+, bir hesap başka bir hesabın şifresini her *sıfırlamaya* çalıştığında oluşur.\n", "adlı kullanıcı hesabı üzerinde parolasını sıfırlama isteğinde bulunmuştur.\n", set()],
            "4725": ["A user account was disabled", "Kullanıcı Hesabı Devre Dışı Bırakılması (Event_ID: 4725)", "+Bu olay+, bir kullanıcı hesabı devre dışı bırakıldığında gözlemlenmektedir.\n", "adlı kullanıcının hesabı devre dışı bırakılmıştır.\n", set()],
            "4726": ["A user account was deleted", "Kullanıcı Hesabı Silinmesi (Event_ID: 4726)", "+Bu olay+, bir kullanıcı hesabı silindiği takdirde oluşmaktadır.\n", "adlı kullanıcı hesabının silindiği tespit edilmiştir.\n", set()],
            "4727": ["A security-enabled global group was created", "Global Domain Grubu Oluşturulması (Event_ID: 4727)", "+Bu olay+, *global* bir domain grubu *oluşturulduğunda* gözlemlenmektedir.\n", "adlı domain grubu oluşturulmuştur.\n", set()],
            "4728": ["A member was added to a security-enabled global group", "Domain Grubuna Yeni Kullanıcının Eklenmesi (Event_ID: 4728)", "+Bu olay+, global domain grubuna yeni kullanıcı eklendiği takdirde oluşmaktadır.\n", "adlı gruba eklenmiştir.\n", set()],
            "4729": ["A member was removed from a security-enabled global group", "Domain Grubundan Kullanıcı Çıkarılması (Event_ID: 4729)", "+Bu olay+, global domain grubundan kullanıcı çıkarıldığı takdirde oluşmaktadır.\n", "adlı grupdan çıkarıldığı tespit edilmiştir.\n", set()],
            "4731": ["A security-enabled local group was created", "Yeni Grup Oluşturulması (Event_ID: 4731)", "+Bu olay+, *local* bir domain grubu oluşturulduğunda gözlemlenmektedir.\n", "adlı domain grubu oluşturulmuştur.\n", set()],
            "4732": ["A member was added to a security-enabled local group", "Yetkili Domain Grubuna Yeni Kullanıcının Eklenmesi (Event_ID: 4732)", "+Bu olay+, local domain grubuna yeni kullanıcı eklendiği takdirde oluşmaktadır.\n", "adlı gruba eklenmiştir.\n", set()],
            "4733": ["A member was removed from a security-enabled local group", "Domain Grubundan Kullanıcı Çıkarılması (Event_ID: 4733)", "+Bu olay+, local domain grubundan kullanıcı çıkarıldığı takdirde oluşmaktadır.\n", "adlı grupdan çıkarıldığı tespit edilmiştir.\n", set()],
            "4741": ["A computer account was created", "Bilgisayar Hesabı Oluşturulması (Event_ID: 4741)", "+Bu olay+, yeni bir bilgisayar hesabı oluşturulduğunda gerçekleşmektedir.\n", "adlı bilgisayar hesabının oluşturulduğu tespit edilmiştir.\n", set()],
            "4743": ["A computer account was deleted", "Bilgisayar Hesabı Silinmesi (Event_ID: 4743)", "+Bu olay+, bir bilgisayar hesabı silindiği takdirde oluşmaktadır.\n", "adlı bilgisayar hesabının silindiği tespit edilmiştir.\n", set()],
            "4754": ["A security-enabled universal group was created", "Yeni Grup Oluşturulması (Event_ID: 4754)", "+Bu olay+, bir *universal* domain grubu oluşturulduğunda gözlemlenmektedir.\n", "adlı grubun oluşturulduğu tespit edilmiştir.\n", set()],
            "4756": ["A member was added to a security-enabled universal group", "Domain Grubuna Yeni Kullanıcının Eklenmesi(Event_ID: 4756)", "+Bu olay+, bir kullanıcı hesabı *universal* domain grubuna eklendiğinde gözlemlenmektedir.\n", "adlı gruba eklendiği tespit edilmiştir.\n", set()],
            "4757": ["A member was removed from a security-enabled universal group", "Domain Grubundan Kullanıcı Çıkarılması(Event_ID: 4757)", "+Bu olay+, bir kullanıcı hesabı universal domain grubundan çıkarıldığında gözlemlenmektedir.\n", "adlı gruptan çıkarıldığı tespit edilmiştir.\n", set()],
            "4764": ["A group’s type was changed", "Grup Türünün değiştirilmesi (Event_ID: 4764)", "+Bu olay+, grubun türü her değiştirildiğinde oluşur. Hem güvenlik hem de dağıtım grupları için oluşturulur. Yalnızca etki alanı denetleyicilerinde oluşturulur.\n", "adlı grubun türünün değiştirildiği tespit edilmiştir.\n", set()],
            "4781": ["The name of an account was changed", "Hesap Adı Değiştirilmesi (Event_ID: 4781)", "+Bu olay+, bir kullanıcı veya hesap adı değiştirildiğinde gözlemlenmektedir.\n", "olarak değiştirilmiştir.\n", set()]
        }

        """
        THERE ARE SOME EVENT ID's IN THIS LIST..

        THE FIRST ELEMENT OF THE LIST AFTER THE EVENT ID IS THE ALERT NAME THAT DEFINES THIS EVENT ID ON CryptoSIM. 
        THE SECOND ELEMENT OF THE LIST AFTER THE EVENT ID IS THE TITLE OF THE TICKET THAT WILL BE OPENED. 
        THE THIRD ELEMENT IS THE SHORT DESCRIPTION ABOUT EVENT ID. 
        THE FOURTH ELEMENT IS THE FINAL STATE OF THE SITUATION. 
        THE LAST ELEMENT IS THE CLUSTER STRUCTURE CREATED TO PREVENT SOME ALERTS FROM REPEATING.
        """
    
    # COMMON CONTENT CREATED FOR THE TICKET TO BE OPENED. YOU CAN CHANGE..
    def events_from_log(self, eventID, eventIDLog):
        events = ""

        for event in self.windows_event_ids[eventID][-1]:
            events += f"{event}\n"

        description = f"""*Tarih:* {self.today_date}\n
*Açıklama:*\n
İlgili tarihte *{eventID} ID'e* sahip Windows olayı oluştuğu gözlemlenmiştir.\n
{self.windows_event_ids[eventID][2]}
*Yapılan Incelemelerde:*\n
{events}*Tavsiye:*\n
İlgili olayın bilginiz dahilinde olduğunu doğrulamanızı öneririz.\n
*Olaya Ait Örnek Log / Loglar:*\n
<pre>
{eventIDLog}
</pre>"""

        # SUBMIT TICKET
        self.submit_ticket(self.windows_event_ids[eventID][1], description, eventID)
        logging.info(f"[+] {eventID} EVENT TICKET IS CREATED.")
    
    def submit_ticket(self, ticket_title, ticket_desc, event_id):
        # DISABLE ALL WARNINGS BECAUSE IT HAS SOME HTTPS PROBLEM
        if not sys.warnoptions:
            warnings.simplefilter("ignore")
            redmine = Redmine(self.ticket_url, requests = {"verify": False}, key='06bdd637723fda09a96119cd63ny3d66aa4e4b99')

            """
            IF YOU DON'T KNOW HOW CAN I REQUEST TO TICKET SYSTEM, 
            YOU SHOULD TO -> https://python-redmine.com/configuration.html
            """

            redmine.issue.create(
                project_id = '7',
                subject = ticket_title,
                tracker_id = 8,
                description = ticket_desc,
                status_id = 1,
                priority_id = 2,
                assigned_to_id = 133,
                custom_fields = [{'id': 12, "value": f"Windows\t{event_id}"}]
            )

    def search_event_id(self):
        # USERNAME AND PASSWORD FOR CryptoSIM
        username = "<USERNAME>"
        password = "<PASSWORD>"

        last_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        first_time = datetime.now() - timedelta(minutes=15)
        first_date = first_time.strftime('%Y-%m-%d %H:%M:%S')

        for event_id in self.windows_event_ids.items():
            search_query = {
                "startDate": first_date, # 15 MINUTES BEFORE
                "endDate": last_date, # CURRENT TIME
                "containStr": event_id[1][0] # NAME OF ALERT
            }

            # REQUEST TO CryptoSIM
            response = requests.post(self.baseURL, auth = HTTPBasicAuth(username, password), 
                        headers = {"Content-Type": "application/json"}, 
                        json = search_query)

            # DATA IS RECEIVED WITH JSON
            result = response.json()
            
            # RESULT CODE IS OK ?
            if result["StatusCode"] == 200:
                # IS THERE DATA ?
                if bool(result["Data"]):
                    for data in result['Data']:
                        event_log = "{recordid}" + data["Log"].split("{recordid}")[-1]
                        eventID = event_log.split("<EventID>")[-1].split("</EventID>")[0]

                        subject_name = event_log.split("<Data Name='SubjectUserName'>")[-1].split("</Data>")[0]
                        target_name = event_log.split("<Data Name='TargetUserName'>")[-1].split("</Data>")[0]
                        # TargetUserName = GroupName

                        subject_domain = event_log.split("<Data Name='SubjectDomainName'>")[-1].split("</Data>")[0]
                        target_domain = event_log.split("<Data Name='TargetDomainName'>")[-1].split("</Data>")[0]

                        added_user = event_log.split("<Data Name='MemberName'>")[-1].split(",")[0][3:]

                        old_username = event_log.split("<Data Name='OldTargetUserName'>")[-1].split("</Data>")[0]
                        new_username = event_log.split("<Data Name='NewTargetUserName'>")[-1].split("</Data>")[0]

                        """
                        THE VALUES HOLDED IN THE ABOVE VARIABLES ARE SOME VALUES 
                        TO BE USED FROM THE LOG CONTAINED IN ALERT ON CryptoSIM.
                        """

                        # IF VALUES ARE NOT EMPTY OR N/A
                        if (subject_name != "" or subject_name != "N/A") and (target_name != "" or target_name != "N/A"):
                            
                            # SEND ALL EVENTS TO THE ABOVE SET.
                            if eventID == "4720" or eventID == "4722" or eventID == "4724" or eventID == "4725" or eventID == "4726" or eventID == "4727" or eventID == "4741" or eventID == "4743" or eventID == "4764" or eventID == "4754" or eventID == "4731":
                                self.windows_event_ids[eventID][-1].add(f"* *{subject_name}* adlı kullanıcı tarafından *{target_name}* {self.windows_event_ids[eventID][-2]}")
                            
                            elif eventID == "4723":
                                self.windows_event_ids[eventID][-1].add(f"* *{target_domain}* domaini altındaki *{target_name}* {self.windows_event_ids[eventID][-2]}")
                            
                            elif eventID == "4728" or eventID == "4729" or eventID == "4732" or eventID == "4733" or eventID == "4756" or eventID == "4757":
                                self.windows_event_ids[eventID][-1].add(f"* *{subject_name}* adlı kullanıcı tarafından *{added_user}* adlı kullanıcı *{target_name}* {self.windows_event_ids[eventID][-2]}")
                            
                            elif eventID == "4781":
                                self.windows_event_ids[eventID][-1].add(f"* {subject_domain}* domaini altındaki *{subject_name}* adlı kullanıcı tarafından eski ismi *{old_username}* olan hesabın adı *{new_username}* {self.windows_event_ids[eventID][-2]}")

                    # IF THE EVENT ID FROM THE LOG AND THE EVENT ID VALUE IN THE WINDOWS EVENT ID LIST EQUAL
                    if event_id[0] == eventID:
                        # SEND TICKET
                        self.events_from_log(event_id[0], event_log)
                        # THIS SWITCH IS IMPORTANT BECAUSE MORE THAN ONE ALERT CAN BE TRIGGERED AS 
                        # WE ARE IN THE CYCLE. TO AVOID THIS SITUATION, THE CONTINUE SWITCH IS USED.
                        continue
                else:
                    logging.warning(f"[-] NO DATA TO ⊱ {event_id[0]} - {str(event_id[1][0]).upper()} RULE ⊰ FOR THIS TIME.")
                    continue
            else:
                logging.error("[-] ERROR STATUS CODE DIFFERENT FROM 200.")
                break
try:
    result = EventIDSubmitter()
    result.search_event_id()
except redminelib.exceptions.AuthError:
    logging.error(f"[-] INVALID USERNAME OR PASSWORD") 
    exit()
except KeyboardInterrupt or KeyError:
    logging.error(f"\n[-] PROGRAM STOPPED BECAUSE CTRL KEY DETECTED.") 
    exit()
except requests.exceptions.ConnectTimeout:
    logging.error(f"\n[-] PROGRAM DID NOT WORK BECAUSE YOU SHOULD CONNECT TO VPN !")
    exit()
except requests.exceptions.ConnectionError:
    logging.error(f"\n[-] CONNECTION FAILD.")
    exit()

# CREATED BY © n3gat1v3o