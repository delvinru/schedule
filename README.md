#  MIREA schedule

---

The bot lives here: [Расписание МИРЭА](https://t.me/scheduleHEIbot)

---

### How to initialize a bot

Don't forget to change the telegram token and password from the database

```bash
echo API_TOKEN=<YOUR_TELEGRAM:TOKEN> > .env
echo POSTGRES_USER=pguser >> .env
echo POSTGRES_PASSWORD=superpassword >> .env
echo POSTGRES_DB=schedule >> .env
```
---

### How to launch a bot

```bash
docker-compose up --build
```
---

### Logging
The bot maintains basic logging for convenient error handling. The logs can be found in the file `src/bot/logs/debug.log`.

---

### TODO:
- [ ] Think about rofl output, xD

### Done:
- [x] Create parser for exams
- [x] Create paging throw weeks
- [x] Create buttons in bottom menu for `today`, `tomorrow`, `week` functions
- [x] Add parser for schedule
- [x] Save user state in database
- [x] Make an interactive menu
- [x] Think about the output in messages
- [x] Think about how to remove garbage from handlers
- [x] Add a schedule display function

---

### Developers/Contacts

* [Kolesnikov Alexey](https://vk.com/delvinru) - UI/UX, Bot logic, App architect
* [Zherebtsov Kirill](https://vk.com/id179026080) -  Schedule parser
