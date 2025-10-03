# Petitions Feature - Comprehensive Video Demo Script

**Duration: ~25 minutes**
**Goal:** Demonstrate deep understanding of Django MVT architecture through a complete petition system implementation with multi-user voting workflow

---

## 📋 Feature Overview & User Story (0:00-2:00)

### Opening Statement (0:00-0:30)
> "Hello, Professor. Today I'll be demonstrating the Movie Petitions feature I've built for the Movies Store application. This feature allows users to request movies they'd like to see added to the store, and other users can vote YES to show support for these requests."

### User Story Context (0:30-1:00)
**The Problem:**
> "The business problem this solves is community engagement. The store owners want to know which movies their customers want. Rather than guessing, we're letting the community drive the inventory decisions through democratic petitions."

**The Solution:**
> "I've implemented a full-stack solution where:
> - ANY visitor can browse petitions (public transparency)
> - AUTHENTICATED users can create new petitions
> - AUTHENTICATED users can vote YES on petitions (once per petition)
> - Vote counts persist and are visible to all users
> - The system prevents abuse through database-level constraints"

### Technical Approach (1:00-2:00)
**Why Django MVT?**
> "I chose to implement this using Django's Model-View-Template (MVT) pattern because:
> 1. **Models** - Define the data structure with built-in ORM and migrations
> 2. **Views** - Handle business logic and permissions cleanly
> 3. **Templates** - Separate presentation from logic for maintainability
>
> This separation of concerns makes the code testable, maintainable, and scalable."

**Technical Highlights:**
- New Django app: `petitions` (modular, reusable)
- 2 models with database-level constraints
- 4 class-based views (leveraging Django's generic views)
- Public/authenticated separation via LoginRequiredMixin
- One vote per user via `unique_together` constraint
- Bootstrap UI matching existing site design
- CSRF protection and message framework integration

---

## 🏗️ Deep Dive: Architecture & Design Decisions (2:00-10:00)

### Part 1: Django Project Structure (2:00-3:00)

**Show file tree in IDE:**
```
petitions/
├── models.py         # Data layer
├── views.py          # Logic layer
├── urls.py           # URL routing
├── admin.py          # Admin interface
├── templates/        # Presentation layer
└── migrations/       # Database schema
```

**Explain Django app philosophy:**
> "Django encourages modularity through apps. The petitions app is completely self-contained - it could be dropped into another Django project with minimal changes. This follows the Single Responsibility Principle - this app does ONE thing: manage movie petitions."

**Integration points with existing project:**
```
@moviesstore/settings.py, line 44
```
> "I registered the app in INSTALLED_APPS, which tells Django to:
> - Discover and run migrations
> - Load templates from the app's template directory
> - Register admin models
> - Make the app's models available to the ORM"

```
@moviesstore/urls.py, line 28
```
> "URL routing uses include() to namespace the app's URLs under /petitions/. This prevents URL conflicts and keeps routing organized."

```
@moviesstore/templates/base.html, line 29
```
> "I added a single navigation link to integrate with the existing UI. Notice I used the namespace 'petitions:list' - this is reverse URL resolution, which prevents hardcoding paths."

---

### Part 2: Data Models - The Foundation (3:00-6:00)

**Open `petitions/models.py` in IDE**

#### Petition Model (lines 6-27) - Design Rationale

**Field choices explained:**
```python
@petitions/models.py, lines 10-14
```

> "Let me explain each field choice:

**1. `title` - CharField(max_length=255):**
> Why CharField? Petitions need a concise, indexed title for display in lists and searches. 255 is the standard max for indexed database fields - going larger would impact query performance.
>
> Why not just use the movie title? The petition title might be more persuasive, like 'Add The Godfather' vs just 'The Godfather'. It gives users creative freedom.

**2. `proposed_movie_title` - CharField(max_length=255):**
> This is separate from the title because we need to track the actual movie being requested. This could be used later to check if the movie already exists in the store, or to auto-create Movie objects when petitions are approved.

**3. `reason` - TextField:**
> TextField allows unlimited length. Users should be able to make a compelling case for why this movie matters. This isn't indexed because we don't need to search within reasons - we search by title.

**4. `created_by` - ForeignKey(User, on_delete=CASCADE):**
> This establishes a many-to-one relationship: each petition has ONE creator, but a user can create MANY petitions.
>
> Why CASCADE? If a user account is deleted, their petitions should be deleted too. This maintains referential integrity. Alternative options like SET_NULL would leave orphaned petitions, which doesn't make sense in our business context.
>
> Why related_name='petitions'? This creates a reverse relationship. Now I can do `user.petitions.all()` to get all petitions by a user. This is crucial for admin views and user profiles.

**5. `created_at` - DateTimeField(auto_now_add=True):**
> auto_now_add means this timestamp is set ONCE when created and never changes. This is different from auto_now which updates on every save. We need to track when petitions were created for sorting and display.

**Meta class and methods:**
```python
@petitions/models.py, lines 16-27
```

**Meta.ordering = ['-created_at']:**
> The minus sign means descending order - newest first. This default ordering is used by ListView queries, so I don't have to specify `.order_by()` everywhere. Shows users the latest petitions first.

**`__str__` method:**
> Returns a human-readable string representation. This appears in:
> - Django admin dropdowns
> - Python shell output
> - Error messages
> I combine title and movie name for maximum clarity.

**`get_absolute_url` method:**
> Best practice for making models aware of their own URL. Uses reverse() to avoid hardcoding paths. This is used by CreateView's default redirect behavior.

**`yes_vote_count` method (lines 25-27):**
> This is a COMPUTED property. I could have used a database field with a counter, but that approach requires complex update logic. Instead, I count related votes in real-time:
> - `self.votes` - uses the related_name from PetitionVote
> - `.filter(yes=True)` - only count YES votes (future-proofs for NO votes)
> - `.count()` - efficient COUNT(*) query in SQL
>
> This ensures the count is ALWAYS accurate and never gets out of sync."

#### PetitionVote Model (lines 30-44) - The Critical Constraint

**Field choices:**
```python
@petitions/models.py, lines 34-37
```

**1. `petition` - ForeignKey(Petition):**
> Many votes can belong to ONE petition. The related_name='votes' lets me do `petition.votes.all()` to get all votes for a petition.

**2. `voter` - ForeignKey(User):**
> Many votes can be cast by ONE user. The related_name='petition_votes' lets me do `user.petition_votes.all()` to see all votes a user has cast.

**3. `yes` - BooleanField(default=True):**
> Currently we only have YES voting, but setting this as a boolean future-proofs the system. If we later add NO voting or abstentions, we won't need to migrate the schema.

**4. `voted_at` - DateTimeField:**
> Tracks when each vote occurred. Useful for analytics, showing recent votes, and detecting suspicious voting patterns.

**THE CRITICAL CONSTRAINT:**
```python
@petitions/models.py, line 40
unique_together = ('petition', 'voter')
```

> "This is the MOST IMPORTANT line in the entire models file. Here's why:

**What it does:**
> Creates a composite unique constraint at the DATABASE level. The combination of (petition, voter) must be unique.

**Why at the database level?**
> 1. **Data Integrity**: Even if my Python code has bugs, the database will NEVER allow duplicate votes
> 2. **Race Conditions**: If two requests from the same user hit the server simultaneously, the database serializes them and rejects the duplicate
> 3. **Direct Database Access**: If someone writes to the database directly (admin panel, shell, external script), the constraint still applies

**How I use it in code:**
> In PetitionYesVoteView (lines 68-78), I TRY to create a vote, and CATCH the IntegrityError if it's a duplicate. This is easier than checking 'does vote exist?' then 'create vote' - that approach has a race condition between the check and the create."

---

### Part 3: Views - Business Logic Layer (6:00-10:00)

**Open `petitions/views.py` in IDE**

#### Design Pattern: Class-Based Views

> "I chose class-based views (CBVs) over function-based views (FBVs) because:
> 1. **DRY Principle**: Django's generic views handle common patterns (list, detail, create)
> 2. **Mixins**: I can add authentication with LoginRequiredMixin in one line
> 3. **Extensibility**: Easy to override specific methods without rewriting everything
> 4. **Code Organization**: Each view class has a clear, single responsibility"

#### PetitionListView (lines 12-19)

```python
@petitions/views.py, lines 12-19
```

**Design decisions:**

**1. Why ListView?**
> ListView is a generic view that handles the common pattern of:
> - Query all objects of a model
> - Paginate them
> - Pass them to a template
> Without ListView, I'd write 20+ lines doing this manually.

**2. Why no authentication?**
> Public transparency is a design goal. Anyone can see what movies are being requested. This encourages participation and builds trust.

**3. Pagination:**
> `paginate_by = 20` automatically handles pagination. Django will:
> - Split results into pages of 20
> - Add page_obj to context
> - Generate Previous/Next page links
> This prevents loading thousands of petitions at once.

**4. context_object_name:**
> Without this, the template would use `object_list`. Using `petitions` makes the template more readable and semantic.

#### PetitionDetailView (lines 22-41)

```python
@petitions/views.py, lines 22-41
```

**Key method: get_context_data (lines 31-41)**

> "I override get_context_data to add custom context:

**Why add user_has_voted?**
> The template needs to know whether to show:
> - 'Vote YES' button (user hasn't voted)
> - 'You Already Voted YES' disabled button (user has voted)
> - 'Log In to Vote' button (anonymous user)

**The logic (lines 33-40):**
```python
if self.request.user.is_authenticated:
    context['user_has_voted'] = PetitionVote.objects.filter(
        petition=self.object,
        voter=self.request.user
    ).exists()
else:
    context['user_has_voted'] = False
```

> - `self.request.user.is_authenticated` - checks if user is logged in
> - `.filter().exists()` - efficient EXISTS query, returns True/False without loading data
> - `self.object` - DetailView provides the current petition automatically
>
> This is a COMPUTED value, not stored in the database. It's calculated fresh on every page load to always be accurate."

#### PetitionCreateView (lines 44-56)

```python
@petitions/views.py, lines 44-56
```

**LoginRequiredMixin (line 44):**
> "This mixin MUST come before CreateView in the inheritance chain. It intercepts the request and:
> - If user is authenticated → continues to CreateView logic
> - If user is NOT authenticated → redirects to login page with ?next= parameter
>
> This is better than @login_required decorator because it works with CBVs."

**fields = ['title', 'proposed_movie_title', 'reason'] (line 50):**
> "I explicitly list which fields appear in the form. Notice `created_by` is NOT here - that's set programmatically in form_valid(). This prevents users from spoofing who created the petition."

**form_valid method (lines 53-56):**
```python
def form_valid(self, form):
    form.instance.created_by = self.request.user
    messages.success(self.request, 'Your petition has been created successfully!')
    return super().form_valid(form)
```

> "This hook runs after form validation passes, but BEFORE saving to the database:
> 1. Set created_by to the current user (auto-attribution)
> 2. Add a success message for user feedback
> 3. Call super() which saves the object and redirects
>
> Why here instead of in the model? Because `request.user` is only available in the view layer, not the model layer."

#### PetitionYesVoteView (lines 59-80) - THE MAGIC

```python
@petitions/views.py, lines 59-80
```

**Why a custom View class instead of a generic view?**
> "Voting is a unique action that doesn't fit CreateView, UpdateView, or any generic pattern. I inherit from base View and implement ONLY the POST method."

**POST-only design:**
```python
def post(self, request, pk):
```
> "Voting should NEVER happen via GET (clicking a link). Why?
> - GET requests should be idempotent and safe (no side effects)
> - Search engines and bots follow GET links - we don't want accidental votes
> - CSRF protection requires POST
> - HTML forms with method='post' prevent casual tampering"

**The idempotent voting logic (lines 68-78):**
```python
try:
    PetitionVote.objects.create(
        petition=petition,
        voter=request.user,
        yes=True
    )
    messages.success(request, f'Your YES vote has been recorded for "{petition.title}"!')
except IntegrityError:
    messages.info(request, 'You have already voted on this petition.')

return redirect('petitions:detail', pk=petition.pk)
```

> "This is an EAFP (Easier to Ask Forgiveness than Permission) pattern:

**Why try/except instead of checking first?**

**Bad approach:**
```python
# DON'T DO THIS - has a race condition
if not PetitionVote.objects.filter(petition=petition, voter=user).exists():
    PetitionVote.objects.create(...)  # ← Another request could create between check and create!
```

**Good approach (what I did):**
> 1. TRY to create the vote
> 2. If it succeeds → show success message
> 3. If it fails with IntegrityError → user already voted, show info message
>
> The database's unique_together constraint GUARANTEES atomicity. Two simultaneous requests will result in one success and one IntegrityError - never two votes.

**IntegrityError handling:**
> I catch IntegrityError specifically (not generic Exception) because:
> - It's the error raised by unique_together violations
> - Other errors (database down, network issues) should bubble up
> - Gives users a friendly message instead of a 500 error

**Return redirect:**
> Always redirect after POST (Post-Redirect-Get pattern). This prevents:
> - 'Resubmit form' warnings when user refreshes
> - Duplicate votes from browser back button"

---

### Part 4: URL Configuration (10:00-11:30)

**Open `petitions/urls.py` in IDE**

```python
@petitions/urls.py, lines 1-11
```

**app_name = 'petitions' (line 4):**
> "This creates a URL namespace. Now I can reference URLs as 'petitions:list' instead of just 'list'. This prevents conflicts if another app also has a 'list' URL."

**URL patterns explained:**

**1. `path('', ...)` → List view:**
> Empty string means this matches `/petitions/` exactly. This is the app's index page.

**2. `path('new/', ...)` → Create view:**
> `/petitions/new/` - I chose 'new' over 'create' because it's more user-friendly in the URL bar.

**3. `path('<int:pk>/', ...)` → Detail view:**
> `<int:pk>` captures an integer from the URL and passes it as `pk` to the view. DetailView automatically uses this to query `Petition.objects.get(pk=pk)`.
>
> Example: `/petitions/5/` shows petition with ID 5.

**4. `path('<int:pk>/vote_yes/', ...)` → Vote view:**
> Nested under the petition URL: `/petitions/5/vote_yes/`
>
> This is RESTful design - the URL structure mirrors the resource hierarchy: petition → vote action.

**Why .as_view()?**
> Class-based views need to be converted to view functions for URL routing. Django's as_view() method does this conversion.

---

### Part 5: Templates - Presentation Layer (11:30-14:00)

**Open `petitions/templates/petitions/list.html` in IDE**

#### Template Inheritance & Django Template Language

**Line 1: `{% extends "base.html" %}`:**
> "This is template inheritance - one of Django's killer features. list.html inherits the entire structure of base.html (navbar, footer, CSS, JS) and only defines the content block. This ensures visual consistency across the entire site without copying code."

**Line 3: `{% block content %}`:**
> "This is where our custom content goes. base.html defines this block, and we override it here."

#### Bootstrap Grid System

**Lines 5-6: Container and row:**
```html
<div class="container my-5">
    <div class="row">
```
> "I'm using Bootstrap's grid system. `container` centers and pads the content, `my-5` adds margin top and bottom. This matches the spacing used in the existing Movies and Cart pages."

#### Conditional Rendering & User Context

**Lines 9-11: Create button for authenticated users:**
```html
{% if user.is_authenticated %}
<a href="{% url 'petitions:create' %}" class="btn btn-primary">Create Petition</a>
{% endif %}
```

> "`user` is automatically available in all templates (via context processors).
> - Authenticated users see the Create button
> - Anonymous users don't see it (though the view still blocks them if they type the URL)
>
> This is progressive disclosure - only show actions users can take."

#### Messages Framework Integration

**Lines 14-21:**
```html
{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
{% endif %}
```

> "Django's messages framework queues one-time messages (success, error, info) across requests.
> - `message.tags` maps to Bootstrap alert types (success, danger, warning, info)
> - `alert-dismissible` makes the X button work
> - Messages automatically clear after being displayed once"

#### Template Loop & Context Variables

**Lines 25-48: Petition list rendering:**
```html
{% for petition in petitions %}
<div class="card">
    <h5>{{ petition.title }}</h5>
    <p><strong>Movie:</strong> {{ petition.proposed_movie_title }}</p>
    <p>{{ petition.reason|truncatewords:30 }}</p>
    <small>Created by {{ petition.created_by.username }} on {{ petition.created_at|date:"M d, Y" }}</small>
    <span class="badge bg-success">{{ petition.yes_vote_count }} YES</span>
</div>
{% endfor %}
```

> "Key template features:
> - `{{ petition.yes_vote_count }}` - calls the model method we defined
> - `{{ petition.created_by.username }}` - follows ForeignKey relationship automatically
> - `|truncatewords:30` - template filter limits text length
> - `|date:"M d, Y"` - formats datetime (Jan 15, 2025)
> - `petition.pk` - primary key for URL generation"

#### URL Reversal in Templates

**Line 42:**
```html
<a href="{% url 'petitions:detail' petition.pk %}">View Details</a>
```

> "Never hardcode URLs like `/petitions/5/`. Instead use `{% url %}` tag:
> - If I change URL patterns, templates still work
> - Works with URL namespaces
> - Handles URL encoding automatically"

---

**Open `petitions/templates/petitions/detail.html` in IDE**

#### CSRF Protection (Line 54)

```html
<form method="post" action="{% url 'petitions:vote_yes' petition.pk %}">
    {% csrf_token %}
    <button type="submit">Vote YES</button>
</form>
```

> "CSRF (Cross-Site Request Forgery) protection:
> - `{% csrf_token %}` generates a hidden input with a unique token
> - Django validates this token on POST requests
> - Without it, malicious sites could trick users into voting
>
> Example attack without CSRF: evil.com has `<img src='moviesstore.com/petitions/1/vote_yes/'>` - if voting was GET, visiting evil.com would cast a vote without the user knowing."

#### Conditional Button States (Lines 47-67)

```html
{% if user.is_authenticated %}
    {% if user_has_voted %}
        <button class="btn btn-success" disabled>You Already Voted YES</button>
    {% else %}
        <form method="post" action="{% url 'petitions:vote_yes' petition.pk %}">
            {% csrf_token %}
            <button type="submit" id="vote-btn">Vote YES</button>
        </form>
    {% endif %}
{% else %}
    <a href="{% url 'accounts.login' %}?next={{ request.path }}">Log In to Vote</a>
{% endif %}
```

> "Three states:
> 1. **Authenticated + Already Voted**: Disabled button (can't vote twice)
> 2. **Authenticated + Not Voted**: Active vote button
> 3. **Anonymous**: Login prompt with ?next= redirect
>
> The `?next={{ request.path }}` parameter tells the login page to redirect back to this petition after successful login."

#### JavaScript Double-Submit Prevention (Lines 94-102)

```javascript
document.getElementById('vote-btn').addEventListener('click', function() {
    this.disabled = true;
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Voting...';
    this.closest('form').submit();
});
```

> "This prevents impatient users from clicking Vote multiple times:
> 1. Disable the button immediately
> 2. Change text to 'Voting...' with spinner
> 3. Submit the form
>
> Even if they bypass this (dev tools), the database constraint still prevents duplicate votes. Defense in depth!"

---

## 🎬 Live Demonstration: Multi-User Workflow (14:00-22:00)

### Introduction (14:00-14:30)
> "Now I'll demonstrate the complete user workflow. I'll create three user accounts and show how the voting system works across different sessions, proving that:
> 1. Vote counts persist in the database
> 2. Each user can only vote once
> 3. The UI updates correctly based on voting state"

### Step 1: Initial Navigation (14:30-15:00)
**Action:**
1. Open browser to `http://127.0.0.1:8000/`
2. Point to navbar showing: About | Movies | **Petitions** | Cart
3. Click **Petitions**

**Talk through:**
> "Notice the Petitions link integrated seamlessly into the existing navigation. This required only one line added to base.html. The link uses Bootstrap's navbar classes to match the existing style."

**Show empty list page:**
> "The page loads successfully even with no petitions. Notice it says 'No petitions yet' with a link to log in or create one. This is better UX than showing a blank page."

---

### Step 2: User A - Alice Creates First Petition (15:00-17:00)

**Registration (15:00-15:30):**
1. Click "Sign Up" in navbar
2. Fill form:
   - Username: `alice`
   - Email: `alice@example.com`
   - Password: `testpass123`
3. Submit

**Talk through registration:**
> "The accounts app was pre-existing. After registration, notice the navbar now shows 'Logout (alice)' - Django's auth system maintains session state via cookies. The user object is now available in all templates and views as `request.user`."

**Create Petition (15:30-16:30):**
1. Navigate to `/petitions/`
2. Click "Create Petition" (now visible because alice is authenticated)
3. Fill form:
   - **Title:** "Add The Shawshank Redemption"
   - **Movie Title:** "The Shawshank Redemption"
   - **Reason:** "This timeless classic about hope and friendship deserves a place in our store. It's one of the highest-rated films of all time and would be a great addition to our drama collection."
4. Submit

**Talk through creation:**
> "Notice the form has three fields - exactly what I specified in PetitionCreateView.fields. The help text comes from the model field definitions.
>
> When I click Create, several things happen:
> 1. Django validates the form (all fields required)
> 2. PetitionCreateView.form_valid() sets created_by = alice
> 3. The Petition is saved to the database
> 4. A success message is queued
> 5. Redirect to the petitions list"

**Show success state (16:30-17:00):**
> "The green success alert appears at the top: 'Your petition has been created successfully!' This message was set in the view and rendered by the template's messages block.
>
> The petition now appears in the list with:
> - Title and movie name
> - Truncated reason (30 words max)
> - Created by alice timestamp
> - **0 YES badge** (no votes yet)"

---

### Step 3: Alice Votes on Her Own Petition (17:00-18:00)

**View Detail (17:00-17:20):**
1. Click "View Details" on the petition
2. Point out all fields displayed:
   - Full title
   - Proposed movie title
   - Complete reason (not truncated)
   - Created by alice with full timestamp
   - **0 YES vote count** in header badge
   - **Vote YES button** (active, not disabled)
   - Recent Votes section (empty)

**Talk through detail view:**
> "The detail view shows the complete petition. Notice the Vote YES button is active - users CAN vote on their own petitions. This is a business logic decision. Some petition systems prevent this, but I chose to allow it since petition creators likely support their own idea."

**Cast Vote (17:20-17:45):**
1. Click "Vote YES"
2. Watch button change to "Voting..." briefly
3. Page reloads

**Talk through voting:**
> "When I clicked Vote YES:
> 1. JavaScript disabled the button and showed a spinner (prevents double-clicks)
> 2. Form submitted POST to `/petitions/1/vote_yes/`
> 3. PetitionYesVoteView.post() ran
> 4. PetitionVote.objects.create() saved the vote to database
> 5. Success message queued
> 6. Redirect back to detail page
>
> The SQL queries were:
> - INSERT INTO petition_vote (petition_id, voter_id, yes, voted_at) VALUES (1, 1, 1, NOW())
> - The unique_together index was checked automatically"

**Show voted state (17:45-18:00):**
> "Now look at the changes:
> - Badge shows **1 YES** (updated from model method)
> - Button is now **disabled and green**: 'You Already Voted YES'
> - Recent Votes shows: alice voted YES with timestamp
> - This proves the vote was saved to the database and the UI correctly reflects voting state"

---

### Step 4: User B - Bob Votes on Alice's Petition (18:00-19:30)

**Logout and Register (18:00-18:30):**
1. Click "Logout (alice)"
2. Click "Sign Up"
3. Register as Bob:
   - Username: `bob`
   - Email: `bob@example.com`
   - Password: `testpass123`

**Talk through session management:**
> "Logging out clears Alice's session cookie. Now I'm registering a completely separate user account. In the database, Alice has user_id=1 and Bob will be user_id=2. Django's auth system handles all session management, password hashing, and CSRF token generation automatically."

**View Petition as Bob (18:30-19:00):**
1. Navigate to `/petitions/`
2. Show list view with badge: **1 YES**
3. Click on petition

**Talk through second user perspective:**
> "Bob can see the petition list and the current vote count (1 YES from Alice). This proves:
> 1. Vote counts persist across sessions
> 2. Vote counts are public (any user can see them)
> 3. The yes_vote_count() method correctly queries the database"

**Bob Votes (19:00-19:30):**
1. Show **Vote YES button is active** (Bob hasn't voted)
2. Click "Vote YES"
3. Show success message
4. Point out changes:
   - Badge: **2 YES** (incremented)
   - Button: **Disabled** (Bob now voted)
   - Recent Votes: Alice and Bob listed

**Talk through second vote:**
> "Bob's vote created a second row in the petition_vote table:
> - petition_id=1, voter_id=2, yes=True
> - The unique_together constraint is satisfied because (1, 2) is different from (1, 1)
> - The vote count query now returns 2
>
> This demonstrates the many-to-many relationship: one petition has many votes, one user can cast many votes (on different petitions)."

---

### Step 5: User C - Charlie Verifies Vote Persistence (19:30-20:30)

**Logout and Register (19:30-20:00):**
1. Logout Bob
2. Register Charlie:
   - Username: `charlie`
   - Email: `charlie@example.com`
   - Password: `testpass123`

**Verify Vote Count Persists (20:00-20:15):**
1. Navigate to `/petitions/`
2. **IMPORTANT**: Point out badge shows **2 YES**
3. Click on petition
4. Show vote count: **2 YES**
5. Show Recent Votes: Alice and Bob

**Talk through persistence verification:**
> "This is critical proof that the votes aren't just in memory or session storage - they're in the SQLite database file. Charlie is a fresh session, never seen this petition before, yet the count shows 2. This is the power of Django's ORM - the query `petition.votes.filter(yes=True).count()` hits the database every time."

**Charlie Votes (20:15-20:30):**
1. Click "Vote YES"
2. Show final state:
   - **3 YES votes**
   - All three users in Recent Votes
   - Button disabled for Charlie

**Talk through third vote:**
> "Now we have three database rows:
> - (petition=1, voter=1) - Alice
> - (petition=1, voter=2) - Bob
> - (petition=1, voter=3) - Charlie
>
> The system scales perfectly. This could be 3 votes or 3000 votes - the logic is identical."

---

### Step 6: Demonstrate Double-Vote Prevention (20:30-22:00)

**UI Prevention (20:30-21:00):**
1. Show disabled button
2. Explain: "The button is disabled in HTML, so normal users can't click it again."

**Developer Bypass Attempt (21:00-21:45):**
1. Open browser DevTools (F12)
2. Inspect the button element
3. Remove `disabled` attribute in HTML
4. Show button is now clickable
5. Click it

**Talk through bypass:**
> "I'm simulating a malicious user who knows how to use browser DevTools. They can modify the client-side HTML to re-enable the button. Let's see what happens when they try to vote again..."

**Show Database Protection (21:45-22:00):**
1. Page reloads
2. Show **info message**: "You have already voted on this petition."
3. Show vote count: **Still 3 YES** (didn't increment to 4)
4. Show Recent Votes: Still shows Charlie's vote only once

**Talk through database protection:**
> "The vote was REJECTED! Here's what happened:
> 1. POST request sent to server (bypassed UI validation)
> 2. PetitionYesVoteView.post() tried to create a vote
> 3. Database INSERT attempted: (petition=1, voter=3)
> 4. **unique_together constraint violated** - this (petition, voter) pair already exists!
> 5. Database raised IntegrityError
> 6. View caught the exception and showed info message
> 7. No vote was created
>
> This is defense in depth:
> - Layer 1: UI disables button (prevents accidents)
> - Layer 2: Template checks user_has_voted (prevents rendering active button)
> - Layer 3: View uses try/except (handles errors gracefully)
> - Layer 4: Database constraint (ULTIMATE protection)
>
> Even if layers 1-3 fail, layer 4 is unbreakable. This is why database constraints are critical for data integrity."

---

## 🔧 Admin Panel Deep Dive (22:00-23:30) [OPTIONAL]

### Accessing Admin (22:00-22:15)
1. Navigate to `/admin/`
2. Login with superuser credentials
3. Show Petitions section

**Talk through:**
> "Django's admin interface is auto-generated from models. I registered both Petition and PetitionVote with custom ModelAdmin classes."

### PetitionAdmin (22:15-22:45)

**Show admin list:**
```
@petitions/admin.py, lines 5-11
```

**Features:**
- List display columns: title, movie, creator, date, vote count
- Search box (searches title, movie, reason)
- Date filter sidebar
- Date hierarchy navigation

**Talk through:**
> "The admin lets staff manage petitions without writing custom views. Notice:
> - `yes_vote_count` appears as a column (callable on model)
> - Search is full-text across multiple fields
> - Date filter helps find petitions from specific time periods
> - Click-through to edit individual petitions"

### PetitionVoteAdmin (22:45-23:15)

**Show votes list:**
```
@petitions/admin.py, lines 14-19
```

**Features:**
- Shows all votes with petition, voter, timestamp
- Filter by yes/no (for future NO votes)
- Search by petition title or voter username

**Talk through:**
> "This is useful for moderation:
> - Detect suspicious voting patterns (same user voting repeatedly on different petitions)
> - Track when votes occurred
> - Manually remove fraudulent votes if needed
> - Generate analytics (which petitions are most popular)"

### Admin Actions Demo (23:15-23:30)

1. Show inline editing
2. Demonstrate you CAN'T create duplicate votes (even from admin)

**Talk through:**
> "Even in the admin, the unique_together constraint applies. If I try to manually create a duplicate vote, I get a database error. The constraint is at the PostgreSQL/MySQL/SQLite level, not just in Django."

---

## 📊 Technical Deep Dive: Design Patterns & Best Practices (23:30-24:30)

### Django Best Practices Implemented

**1. MVT Separation of Concerns:**
> - Models: Pure data logic, no business rules
> - Views: Business logic, no HTML generation
> - Templates: Presentation, no complex logic

**2. DRY (Don't Repeat Yourself):**
> - Template inheritance (base.html)
> - Generic views (ListView, DetailView)
> - Model methods (yes_vote_count, __str__)

**3. Security:**
> - LoginRequiredMixin for authentication
> - CSRF tokens on all forms
> - Database constraints prevent data corruption
> - POST for state-changing operations
> - SQL injection prevented by ORM

**4. User Experience:**
> - Messages framework for feedback
> - Progressive disclosure (show actions user can take)
> - Clear error messages (not technical stack traces)
> - Responsive Bootstrap UI

**5. Scalability:**
> - Efficient queries (no N+1 problems)
> - Pagination prevents large result sets
> - Database indexes (unique_together creates index)
> - Computed properties (vote count not denormalized)

**6. Maintainability:**
> - Clear model relationships
> - Docstrings on complex methods
> - Semantic naming (PetitionYesVoteView, not VoteView)
> - URL namespaces prevent conflicts
> - Modular app structure

---

## 🎯 Conclusion & Learning Outcomes (24:30-25:00)

### What I Demonstrated

> "In this video, I've shown:

**Technical Skills:**
- Django MVT architecture implementation
- ORM with complex relationships (ForeignKey, unique_together)
- Class-based views with mixins
- Template inheritance and Django Template Language
- URL routing with namespaces
- Forms with validation and CSRF protection
- Messages framework integration
- Admin interface customization
- Database migrations

**Software Engineering Principles:**
- Defense in depth (multiple validation layers)
- Idempotent operations (voting)
- Separation of concerns (MVT)
- DRY principle (generic views, template inheritance)
- RESTful URL design
- Progressive enhancement (JavaScript optional)

**Problem-Solving:**
- Race condition prevention (try/except pattern)
- User state management across sessions
- Multi-user workflows
- Data integrity constraints

### Why This Matters

> "This petitions feature is more than just a form and a vote button. It demonstrates understanding of:
> - How web applications manage state
> - How databases ensure consistency
> - How authentication and authorization work
> - How to build scalable, maintainable code
> - How to think about user experience and security together

These are the foundations of professional web development, and Django's MVT pattern makes them accessible while enforcing best practices."

---

## 📝 Grading Rubric Alignment

| Requirement | Implementation | File Reference |
|-------------|----------------|----------------|
| Separate petitions page | ✅ PetitionListView | `views.py:12-19`, `urls.py:7` |
| Create petition form | ✅ PetitionCreateView | `views.py:44-56`, `urls.py:8` |
| Petition detail page | ✅ PetitionDetailView | `views.py:22-41`, `urls.py:9` |
| YES voting | ✅ PetitionYesVoteView | `views.py:59-80`, `urls.py:10` |
| One vote per user | ✅ unique_together | `models.py:40` |
| Vote count display | ✅ yes_vote_count() | `models.py:25-27` |
| Anonymous user handling | ✅ LoginRequiredMixin + template | `views.py:44,59`, `detail.html:63` |
| Multi-user workflow | ✅ Demonstrated live | Video 15:00-22:00 |
| Database persistence | ✅ SQLite with migrations | `migrations/0001_initial.py` |
| Admin integration | ✅ ModelAdmin classes | `admin.py:5-19` |
| Code quality | ✅ Docstrings, type hints, PEP8 | All Python files |
| UI consistency | ✅ Bootstrap, extends base.html | All template files |

---

## 🗑️ Rollback Instructions

### Quick Removal (if needed for testing)
```bash
# 1. Revert database
python manage.py migrate petitions zero

# 2. Remove from settings
# Comment out 'petitions' in INSTALLED_APPS

# 3. Remove from URLs
# Comment out path('petitions/', include('petitions.urls'))

# 4. Remove from nav
# Comment out Petitions link in base.html line 29

# 5. Delete app
rm -rf petitions/
```

---

## 📚 Additional Resources

**Django Documentation:**
- Models: https://docs.djangoproject.com/en/5.0/topics/db/models/
- Views: https://docs.djangoproject.com/en/5.0/topics/class-based-views/
- Templates: https://docs.djangoproject.com/en/5.0/topics/templates/

**Code Location:**
- All petition code: `/petitions/` directory
- Integration points: 3 files modified (settings.py, urls.py, base.html)
- Database: `db.sqlite3` (tables: petitions_petition, petitions_petitionvote)

**Testing Commands:**
```bash
# Check for issues
python manage.py check

# View SQL for migration
python manage.py sqlmigrate petitions 0001

# Open Django shell
python manage.py shell

# Test in shell:
from petitions.models import Petition, PetitionVote
Petition.objects.all()
```

---

**Total Duration: 25 minutes**

**Video Structure:**
- 0:00-2:00: Overview & User Story (2 min)
- 2:00-10:00: Architecture Deep Dive (8 min)
- 10:00-14:00: Templates & Frontend (4 min)
- 14:00-22:00: Live Multi-User Demo (8 min)
- 22:00-23:30: Admin Panel (1.5 min)
- 23:30-25:00: Conclusion & Learning Outcomes (1.5 min)

**Good luck with your presentation, Professor! 🎓**
