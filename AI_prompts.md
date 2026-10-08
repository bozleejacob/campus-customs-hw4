# Prompt Log

1. Can we start a new project titled hw4? Make a folder in the AI Foundations folder

2. It's a new separate project, keep hw4

3. @"C:\Users\bozle\Downloads\data (1).zip" Take the components of the zip file and unzip it, including homework four folder.

4. We have in previous projects created an AI prompts.md file to record all prompts throughout the homework4.

5. create a folder in Home 4 called Problem 2. Analyze the database. four called problem two, analyze the database, period. In problem two folder, include a file called output slash harness.md. Include in this output file a description of each table and its fields. with one short line on why each field matters for the shop.

6. Move to problem three. Create a folder called problem three. Build the campus customs website.

7. stop

8. That was just the title of the problem. No need to start yet

9. Start by creating a scaffold. Scaffold a React plus Vite plus TypeScript front end for campus customs. We want to put a navigation bar at the top that links to these main pages. Home, products, about us, login, create account. Pull campus custom style wording from yalebulldogblue.com for home and about us. Do not use their exact wording, but use my voice.

10. on the products page, I want it to show product images from the catalog using images from our database with basic product info to include name, price, and a short description. Make sure each product opens a single page with a large image on one side and full product text on the other with the description, price, size, stock when you have it. If I were to click a card on the products, it it it it it the shop label. At a chat interface in the bottom right of the site, it does not need to talk to an agent yet, but I need a stub that will call your back in later if enough. That will call your back in later is enough for this problem. I will need a small API soon to read the database, but it's fine to start a simple, fast API app in backend slash main.py just to serve products and images. Then we'll grow into an agent backend in problem five.

11. Great. Let's move to problem four. Create a folder called problem four - create account and login., colon, create account and login.

12. All right. So we want to build a normal create account login flow. So the create account button will have first name, last name, email, and password. Login will have email and password. New accounts generated will go into our users table and make sure to store passwords securely so hackers cannot access them. The database already has a test user. See if we can use that test user, the test at camp customs, campuscustoms.yale.edu password. And see if that user can log in. After all that, update output slash harness.md with how the authorization works and what we store for a user and how passwords are protected. Go.

13. Let's start problem five. Create a folder called problem five pedantic AI agent backend.

14. We're going to want to build the shop chatbot as a pydantic AI agent behind FastAPI. Put the API app in backend/main.py This is the file that we're going to run with uvicorn. Keep the agent at these four files next to it. backend/prompts/prompt.md. backend/agent.py. backend/tools.py. backend/models.py. And in main.py, I want to expose a chat route so a message from the website gives a reply from the agent. And I'm pretty sure you're going to need my AI model API key for the agent, which we should have saved. We want to use Luna. We're going to want to put campus customs voice and safety basics into prompts/prompt.md. And we'll want to start or update types in models.py for chat replies as needed. In output/harness.md, note how the front end talks to FastAPI and how the agent is loaded. We want to make sure in the end that the backend runs from the backend folder with this code.

uvicorn main:app --reload --port 8000

15. [clarification] Everything that says slash means "/" and dot means "." from above

16. [AskUserQuestion] The website already has a running backend (Problem 3's backend/main.py, port 8000) serving /products and /auth. Should the new chat agent live in that same backend, or in a brand-new standalone backend folder inside Problem 5? → Answered: Extend existing backend.

17. Let's start problem six

18. Problem 6 - Tools product info and stock. Create the folder

19. All right, we're going to want to give the agent tools to look up real information from the Campus Customs database, the one that we have in our folder. It's going to look up the product description, price, and how many are in stock. The agent needs to use this database and should not invent prices or quantities. If a size is out of stock, the agent should say so. We're going to want to expand our prompts/prompt.md file, so that our agent knows to call upon these tools for price and stock questions. Add or update the return types in models.py. And then in our output/harness.md file, I want us to list the tools and explain which model fields you chose for lookup results and why.

20. Let's start problem seven. Create problem 7 folder. Problem 7 - Chat search that updates the page

21. All right. We want to add a new feature for a site. So when a customer asks about a type of item, the agent should search the catalog and I want our website to dynamically show those matching items as product cards. Include image, name, price, and short description. Just want to note that after we create this new feature, I want to make sure the same single item page behavior we built in problem three still works. Should still open the detail view with a large image and description when it's clicked. Update our prompts.md file and output harness.md file so it's clear how search results reach our page.

22. Let's start problem eight. Create a problem 8 - customer memory folder.

23. Now we want to have data on our customers. When a shopper is logged in, I want the agent to save the chat history in the database, in an appropriate table, so it can be reloaded when that shopper logs back on. The agent should know who is chatting by name and email, so that it can be called upon again. Also, I want to pass enough page context that if someone is on a product page and asks, "do you have this in pink?", the agent knows which item they mean. Guests can still chat, but history only needs to persist for logged-in users — if someone's on a guest account, we don't need to record their data. Document in output/harness.md how the user chat history is stored, what customer fields the agent sees, and how the page context is passed.

24. Start a problem 9. Create folder "problem 9 - usability improvements"

25. We recommend two front-end usability improvements and two agent back-end usability improvements.

26. [clarification, mid-turn] Can you recommend

27. go ahead with these four. Can you make an output/usability.md file in the file describe each improvement and why it helps the shopper or the business? Use one sentence. One sentence per improvement.

28. Let's start problem 10. Create folder: Problem 10 - Style the website

29. Use Yale blue and white as the main colors, clean modern layout. Use standard fonts but maybe elitist title fonts

30. Write output/design.md: Put "Made the website Yale blue and white with clean modern layout. Used standard fonts for most text and fancier texts for titles"

31. Let's start problem 11

32. Problem 11: Site testing (app check). Create folder

33. I need to test the live site and document it in output/app_check.html. The output needs to be a page I can double-click open.

34. [mid-turn] Can you open the site so I can look at it

35. Can you add these screenshots to output/app_check.html? Include the descriptions: Chat shows inventory level of the Big Yale Hoodie. Chat shows the dynamic search result. [two screenshots attached]

36. [mid-turn clarification] Autoscroll feature added in problem 9 [note tying the hoodie-stock screenshot to the Problem 9 auto-scroll improvement]

37. Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png)

38. Let's start problem 12. Create folder: Problem 12 - Audit trail, safety, finish harness

39. Make output/audit_trail.json. I want this JSON file to keep track of the agent loop activity, include time, tool name used, results, and reasons for stopping. Do not wipe in between runs. Keep the data. Additionally, please recommend safety rules for the agent and put them in prompts/prompt.md. Lastly, we need to complete output/harness.md so it's clear how our system works. Include model fields in models.py and why we chose them, tools and abilities, safety rules, and specifications. Examples of specifications: loop limits, result caps, models, how to run front and back ends.

40. alright. stop recording prompts
