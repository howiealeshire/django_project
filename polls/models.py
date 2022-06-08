import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
>> Question.objects.all()
<QuerySet []>
>> from django.utils import timezone
>> q = Question(question_text="What's new?", pub_date=timezone.now())
>> q.save()
>> q.id
1
>> q.question_text
"What's new?"
>> q.pub_date
datetime.datetime(2012, 2, 26, 13, 0, 0, 775217, tzinfo=<UTC>)
>> q.question_text = "What's up?"
>> q.save()
>> Question.objects.all()
<QuerySet [<Question: Question object (1)>]>\
>> Question.objects.filter(id=1)
<QuerySet [<Question: What's up?>]>
>> Question.objects.filter(question_text__startswith='What')
<QuerySet [<Question: What's up?>]>
q = Question.objects.get(pk=1)
>> q.choice_set.create(choice_text='Not much', votes=0)
<Choice: Not much>
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    """
    >> Choice.objects.filter(question__pub_date__year=current_year)
<QuerySet [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]>
    >> c = q.choice_set.filter(choice_text__startswith='Just hacking')
    >> c.delete()
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Person(models.Model):
    """
    Queries ran:
        >> p = Person(name="Fred Flintstone", shirt_size="L")
        >> p.save()
        >> p.shirt_size
            'L'
        >> p.get_shirt_size_display()
            'Large'

    # Find all the members of the Beatles that joined after 1 Jan 1961
    >> Person.objects.filter(
...     group__name='The Beatles',
...     membership__date_joined__gt=date(1961,1,1))
    <QuerySet [<Person: Ringo Starr]>
    """
    SHIRT_SIZES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    )
    name = models.CharField(max_length=60,)
    shirt_size = models.CharField(max_length=1, choices=SHIRT_SIZES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True)

    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        import datetime
        if self.birth_date < datetime.date(1945, 8, 1):
            return "Pre-boomer"
        elif self.birth_date < datetime.date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"

    @property
    def full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)


class Group(models.Model):
    """
     >> Group.objects.filter(members__name__startswith='Paul')
    <QuerySet [<Group: The Beatles>]>
    """
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through='Membership')

    def __str__(self):
        return self.name


class Membership(models.Model):
    """
    Membership acts as an intermediary between Person and Group. The many to many relationship exists between
    Person and Group,
    and you can add extra fields to track as well.

    >> ringo = Person.objects.create(name="Ringo Starr")
    >> paul = Person.objects.create(name="Paul McCartney")
    >> beatles = Group.objects.create(name="The Beatles")
    >> m1 = Membership(person=ringo, group=beatles,
    ...     date_joined=date(1962, 8, 16),
    ...     invite_reason="Needed a new drummer.")
    >> m1.save()
    >> beatles.members.all()
    <QuerySet [<Person: Ringo Starr>]>
    >> ringo.group_set.all()
    <QuerySet [<Group: The Beatles>]>
    >> m2 = Membership.objects.create(person=paul, group=beatles,
    ...     date_joined=date(1960, 8, 1),
    ...     invite_reason="Wanted to form a band.")
    >> beatles.members.all()
    <QuerySet [<Person: Ringo Starr>, <Person: Paul McCartney>]>
    >> beatles.members.add(john, through_defaults={'date_joined': date(1960, 8, 1)})
    >> beatles.members.create(name="George Harrison", through_defaults={'date_joined': date(1960, 8, 1)})
    >> beatles.members.set([john, paul, ringo, george], through_defaults={'date_joined': date(1960, 8, 1)})
    >> # Beatles have broken up
    >> beatles.members.clear()
    >> # Note that this deletes the intermediate model instances
    >> Membership.objects.all()
    <QuerySet []>
    >> ringos_membership = Membership.objects.get(group=beatles, person=ringo)
    >> ringos_membership.date_joined
    datetime.date(1962, 8, 16)
    >> ringos_membership.invite_reason
    'Needed a new drummer.'
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)


class Ox(models.Model):
    horn_length = models.IntegerField()

    class Meta:
        ordering = ["horn_length"]
        verbose_name_plural = "oxen"


class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)


class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()


class Runner(models.Model):
    """
    "You can also use enumeration classes to define choices in a concise way"
    https://docs.djangoproject.com/en/4.0/topics/db/models/
    """
    MedalType = models.TextChoices('MedalType', 'GOLD SILVER BRONZE')
    name = models.CharField(max_length=60)
    medal = models.CharField(blank=True, choices=MedalType.choices, max_length=10)


class Fruit(models.Model):
    """
    The primary key field is read-only. If you change the value of the primary key on an existing object
    and then save it, a new object will be created alongside the old one.
    https://docs.djangoproject.com/en/4.0/topics/db/models/

    >> fruit = Fruit.objects.create(name='Apple')
    >> fruit.name = 'Pear'
    >> fruit.save()
    >> Fruit.objects.values_list('name', flat=True)
    <QuerySet ['Apple', 'Pear']>

    """
    name = models.CharField(max_length=100, primary_key=True)


class Manufacturer(models.Model):
    # ...
    pass


class Car(models.Model):
    # a Manufacturer makes multiple Cars, but each Car has only one Manufacturer
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)


class Topping(models.Model):
    # ...
    pass


class Pizza(models.Model):
    # a Pizza has many toppings, and a topping can be on multiple pizzas
    toppings = models.ManyToManyField(Topping)


class Blog1(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def save(self, *args, **kwargs):
        # do_something()
        super().save(*args, **kwargs)  # Call the "real" save() method.
        # do_something_else()

    """
        
      def save(self, *args, **kwargs):
        if self.name == "Yoko Ono's blog":
            return # prevent save
        else:
            super().save(*args, **kwargs)  # Call the "real" save() method.
    """

"""
Queries docs https://docs.djangoproject.com/en/4.0/topics/db/queries/ used below models
"""

class Blog(models.Model):
    """
    #Saving changes to objects:
    from polls.models import Blog
    >> b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
    >> b.save()
    >> b.name = "New name"
    >> b.name
    'New name'
    #Saving ForeignKey and ManyToManyField fields
     from polls.models import Blog, Entry


    """
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def __str__(self):
        return self.name



class Entry(models.Model):
    # e = Entry(blog=b,headline="hl_test",body_text="body_test",pub_date=datetime.now(),number_of_comments=2,number_of_pingbacks=1,rating=5)
    # e.save()
    # e.authors.set([a,a])
    """
    >> entry = Entry.objects.get(pk=1)
    >> cheese_blog = Blog.objects.get(name="Cheddar Talk")
    >> entry.blog = cheese_blog
    >> entry.save()
    joe = Author.objects.create(name="Joe")
    >> entry.authors.add(joe)   #use add for updating many to many fields

    >> all_entries = Entry.objects.all() #get queryset of all entities from a table
    >> all_entries
    <QuerySet [<Entry: hl_test>]>
    >> Entry.objects.filter(pub_date__year=2022) # keyword argument queries are "ANDed" together
    <QuerySet [<Entry: hl_test>]>

    # Update all the headlines with pub_date in 2007.
    Entry.objects.filter(pub_date__year=2007).update(headline='Everything is the same')

    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    pub_date = models.DateField()
    mod_date = models.DateField(default=datetime.date.today)
    authors = models.ManyToManyField(Author)
    number_of_comments = models.IntegerField(default=0)
    number_of_pingbacks = models.IntegerField(default=0)
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.headline

class QObjects:
    """
     Dog.objects.filter(data__contained_by={'breed': 'collie', 'owner': 'Bob'}) #contained by breed val AND owner val
     Q objects are for more complex queries (e.g. OR statements)
     Q(question__startswith='What') #LIKE query
     Q(question__startswith='Who') | Q(question__startswith='What')
        -> Equivalent to WHERE question LIKE 'Who%' OR question LIKE 'What%'

    """
# =================================================================================
# Aggregate Expressions

class Author(models.Model):
    # a = Author(name="Bob",email="test.email@email.org")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()

class Publisher(models.Model):
    name = models.CharField(max_length=300)

class Book(models.Model):
    name = models.CharField(max_length=300)
    pages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    pubdate = models.DateField()

class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)

# Most Common

"""
# Total number of books.
>>> Book.objects.count()
2452

# Total number of books with publisher=BaloneyPress
>>> Book.objects.filter(publisher__name='BaloneyPress').count()
73

# Average price across all books.
>>> from django.db.models import Avg
>>> Book.objects.all().aggregate(Avg('price'))
{'price__avg': 34.35}

# Max price across all books.
>>> from django.db.models import Max
>>> Book.objects.all().aggregate(Max('price'))
{'price__max': Decimal('81.20')}

# Difference between the highest priced book and the average price of all books.
>>> from django.db.models import FloatField
>>> Book.objects.aggregate(
...     price_diff=Max('price', output_field=FloatField()) - Avg('price'))
{'price_diff': 46.85}

# All the following queries involve traversing the Book<->Publisher
# foreign key relationship backwards.

# Each publisher, each with a count of books as a "num_books" attribute.
>>> from django.db.models import Count
>>> pubs = Publisher.objects.annotate(num_books=Count('book'))
>>> pubs
<QuerySet [<Publisher: BaloneyPress>, <Publisher: SalamiPress>, ...]>
>>> pubs[0].num_books
73

# Each publisher, with a separate count of books with a rating above and below 5
>>> from django.db.models import Q
>>> above_5 = Count('book', filter=Q(book__rating__gt=5))
>>> below_5 = Count('book', filter=Q(book__rating__lte=5))
>>> pubs = Publisher.objects.annotate(below_5=below_5).annotate(above_5=above_5)
>>> pubs[0].above_5
23
>>> pubs[0].below_5
12

# The top 5 publishers, in order by number of books.
>>> pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]
>>> pubs[0].num_books
1323
"""


# =============================================
# F Expressions

"""
reporter = Reporters.objects.get(name='Tintin')
reporter.stories_filed = F('stories_filed') + 1 #F expressions access the DB directly, without loading into memory
reporter.save()

reporter.refresh_from_db() #now we can access the updated value

Reporter.objects.all().update(stories_filed=F('stories_filed') + 1) #update all of these at once, without loading into memory,
                                                                    #without looping through and updating, etc. 
                                                                    #F expressions also avoid race conditions that could
                                                                    #otherwise occur in Python-side saving and updating
                                                                    
                                                                    
"""

# ==============================================
# Func

"""
#Func encapsulates all DB functions (e.g. COALESCE, LOWER, etc.)
from django.db.models import F, Func

queryset.annotate(field_lower=Func(F('field'), function='LOWER'))

or they can be used to build a library of database functions:

class Lower(Func):
    function = 'LOWER'

queryset.annotate(field_lower=Lower('field'))

"""
