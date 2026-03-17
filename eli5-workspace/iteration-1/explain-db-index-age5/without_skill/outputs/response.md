# ELI5: What Is a Database Index?

Imagine you have a really big book full of names -- like a phone book with thousands and thousands of names in it.

Now, someone asks you: "What is Jamie's phone number?"

You *could* start at the very first page and read every single name, one by one, until you finally find Jamie. That would take a really long time, especially if Jamie's name is near the end of the book.

But phone books have a trick: all the names are in ABC order! So you can skip straight to the "J" section, and find Jamie super fast without reading the whole book.

A **database index** is basically that same trick, but for a computer.

A database is like a giant list of information (names, ages, scores, whatever). When you ask the computer to find something in that list, it could look at every single item one by one -- but that is slow. An index is a special shortcut the computer makes ahead of time that says "here is where everything is, sorted in a handy order." That way, when you ask for something, the computer can jump right to it instead of checking every single thing.

**The trade-off:** The index takes up a little extra space (just like the alphabetical table of contents at the back of a book takes up extra pages), and every time you add new stuff to the database, the index has to be updated too. But the speed boost you get when searching is usually worth it.

**In short:** A database index is like the alphabetical ordering in a phone book -- it helps the computer find what you are looking for way, way faster.
