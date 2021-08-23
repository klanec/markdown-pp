# REPORT

## Executive Summary 

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.

## Summary of all findings

|   CVSS | summary                                                 | implication                                                        | solution                                                                                                                                                                                                                                |
|-------:|:--------------------------------------------------------|:-------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |

and using the pandas and tabulate library::

|   CVSS | summary                                                 | implication                                                        | solution                                                                                                                                                                                                                                |
|-------:|:--------------------------------------------------------|:-------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |

## Network Findings

### Summary of Network Findings
|   CVSS | summary                                                 | implication                                                        | solution                                                                                                                                                                                                                                |
|-------:|:--------------------------------------------------------|:-------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |
|      0 | Lorem ipsum dolor sit amet, consectetur adipiscing elit | sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. |

### Finding 1
|   CVSS | references                                                                      | author                                        |
|-------:|:--------------------------------------------------------------------------------|:----------------------------------------------|
|      0 | <ul><li>BID-123</li><li>CVS-2018-8079</li><li>CWE-123</li><li>CVE-345</li></ul> | <ul><li>John Smith</li><li>Jane Doe</li></ul> |


#### Summary

lol

#### Implication

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

#### Solution

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam.

#### Reproduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.

#### Affects

- http://192.168.0.1/index.html
- http://192.168.0.2/index.html

### Finding 2
|   CVSS | references                                                                      | author                                        |
|-------:|:--------------------------------------------------------------------------------|:----------------------------------------------|
|      0 | <ul><li>BID-123</li><li>CVS-2018-8079</li><li>CWE-123</li><li>CVE-345</li></ul> | <ul><li>John Smith</li><li>Jane Doe</li></ul> |


#### Summary

lol

#### Implication

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

#### Solution

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam.

#### Reproduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.

#### Affects

- http://10.10.0.1/index.html
- http://10.10.0.2/index.html

### Finding 3

this one has no frontmatter. Lets see what it does.


<span style="color:FireBrick">ERROR: !FRONTMATTER tags.network, CAUSE_ERROR_WRONG_STRUCTURE(CVSS, summary, implication, solution)</span> <!-- !ERROR:  Requested data structure not recognized -->

<span style="color:FireBrick">ERROR: !FRONTMATTER tags.NOTFOUND, CAUSE_ERROR_NO_DATA(CVSS, summary, implication, solution)</span> <!-- !ERROR:  No matching data found in frontmatter -->

<span style="color:DodgerBlue">COMMENT: This is a default Blue comment</span>

<span style="color:Green">COMMENT: This is a Green comment</span>

<span style="color:OrangeRed">TODO: This is a default Red TODO tag</span>

<span style="color:Purple">TODO: This is a pretty Purple TODO tag</span>
