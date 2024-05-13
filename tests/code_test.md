{loc}

# Section A
Id pariatur doloribus aut animi commodi. Voluptatem distinctio possimus vero temporibus totam ratione necessitatibus delectus. Consequuntur sapiente quidem accusamus. Quidem sunt qui pariatur.

Est aliquam asperiores est expedita numquam molestiae. Voluptates et quas odio magni ipsum excepturi. Quidem distinctio autem dolor quis autem enim earum. Aliquid omnis sint eos rerum. Repudiandae architecto vitae ipsam in consequatur. Dolores quaerat qui ad.

Tempora sunt est odio dolorem aut earum deleniti maiores. Vel facilis reiciendis hic magnam. Adipisci quaerat molestias ipsum. Commodi aut illum vero ipsum dignissimos velit esse. Qui omnis voluptates earum.

<!-- we could reuse the definition of split links for defining header description of code blocks ??? -->

<!-- [below shows code block for]: -->
``` [Code]
a = a+1
c = c*a
```

``` [Code]
a = a+1

c = c*a
```

<!--
` `` [More detailed code] { .html }
a = a+1
c = c*a
` ``

` `` { .html }
a = a+1
c = c*a
` ``
-->

Pariatur at optio voluptatem minima voluptates. Ea consequuntur vel ut nostrum et nostrum. Laudantium nulla quo quisquam neque.

Ullam impedit quos ipsum nulla neque. Culpa quas voluptas officiis itaque. Est reprehenderit ipsam id. Praesentium dignissimos deleniti porro ex. Blanditiis autem cupiditate porro dolorem possimus iste fugit. Aut iusto ea placeat adipisci itaque.

# Codes
The code is below.

## Standalone code block
```
standalone
code
block
```

## Standalone code block with space at the beginning
```

standalone
code
block
```

## Standalone code block with space in the middle
```
standalone

code
block
```

## Standalone code block with space at end
```
standalone
code
block

```

## Code
``` [Yet another Code 1]
a = a + 1
b = b * 2
bla
s {artefact:1}
{artefact:2}
{artefact:3} s
bla2 {artefact:4} foo2 
bla3 {artefact:5} foo3 {artefact:6} bar3
foo
bar
```

## Code starting with artefact
``` [Yet another Code 2]
{artefact:1}
bla2 {artefact:2} foo2
bla3 {artefact:3} foo3 {artefact:4} bar3
foo
bar
```

## Code ending with artefact
``` [Yet another Code 3]
bla2 {artefact:2} foo2
bla3 {artefact:3} foo3 {artefact:4} bar3
foo
bar
{artefact:5}
```

## Code starting and ending with artefact
``` [Yet another Code 4]
{artefact:1}
bla2 {artefact:2} foo2
bla3 {artefact:3} foo3 {artefact:4} bar3
foo
bar
{artefact:5}
```

## Code starting and ending with space plus artefact
``` [Yet another Code 5]

{artefact:1}
bla2 {artefact:2} foo2
bla3 {artefact:3} foo3 {artefact:4} bar3

foo
bar
{artefact:5}

```

## Code starting with artefact with space line
``` [Yet another Code 6]
{artefact:1}
bla2 {artefact:2} foo2
bla3 {artefact:3} foo3 {artefact:4} bar3

foo
bar
```

## Code with space lines
``` [Yet another Code 7]
bla2

foo

bar
```

## Code element without decoding
<!--{code:code block direct}-->
```
test
test2
test3
```

## Inline code
Inline code `c = d+e` test.
