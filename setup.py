from setuptools import setup

setup(
	name='richtextpy',
	version='0.1',
	url='http://github.com/sachinrekhi/richtextpy',
	description='An operational transformation library for rich text documents',
	keywords='operational transformation type rich text',
	classifiers=[
		'Programming Language :: Python :: 2.7',
		'License :: OSI Approved :: MIT License',
	],
	author='Sachin Rekhi',
	author_email='sachin.rekhi@gmail.com',
	license='MIT',
	packages=['richtextpy'],
	install_requires=[
		'diff_match_patch',
	],
	test_suite='tests',
	include_package_data=True,
	zip_safe=False
)
