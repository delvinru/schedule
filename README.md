#  MIREA schedule
---

#### How initialize bot

Don't forget to change the telegram token and password from the database

```bash
echo API_TOKEN=<YOUR_TELEGRAM:TOKEN> > .env
echo POSTGRES_USER=pguser >> .env
echo POSTGRES_PASSWORD=superpassword >> .env
echo POSTGRES_DB=schedule >> .env
```

### How start bot

```bash
docker-compose up --build
```



### TODO:
- [✓] Add parser for schedule
- [ ] Save user state in database
- [ ] Make an interactive menu
- [ ] Think about the output in messages